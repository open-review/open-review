from collections import namedtuple, defaultdict, OrderedDict
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db import models
from django.db.models import Sum
from django.conf import settings

__all__ = ["Review", "Vote", "ReviewTree", "set_n_votes_cache"]

def set_n_votes_cache(reviews):
    """
    Set caches of n_downvotes, n_upvotes on `reviews`.

    @param reviews: reviews which votes to cache
    @type reviews: iterable of Review objects
    """
    votes = Vote.objects.filter(review__in=reviews).values_list("review").annotate(n=Sum("vote"))
    upvotes = dict(votes.filter(vote__gt=0))
    downvotes = dict(votes.filter(vote__lt=0))

    for review in reviews:
        review._n_downvotes = -downvotes.get(review.id, 0)
        review._n_upvotes = upvotes.get(review.id, 0)

ReviewTree = namedtuple('ReviewTree', ['review', 'level', 'children'])

REVIEW_FIELDS = {"text", "rating", "timestamp"}

class Review(models.Model):
    """
    A review can either be a 'real' review of a paper (parent == None) or a meta-review, which is
    referred to as a comment in the user interface (parent != None).
    """
    text = models.TextField(verbose_name="contents", null=True)
    rating = models.SmallIntegerField(default=-1)
    timestamp = models.DateTimeField(auto_now_add=True)

    poster = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="reviews", null=True)
    paper = models.ForeignKey("main.Paper", related_name="reviews")
    parent = models.ForeignKey("self", null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._n_upvotes = None
        self._n_downvotes = None
        self._n_comments = None

        # If cache() is called this is a defaultdict(list) with
        # review_id -> [children_ids].
        self._reviews_children = None

        # If cache() is called, this contains a review_id -> Review mapping
        self._reviews = None

    @classmethod
    def latest(cls):
        return Review.objects.order_by('-timestamp')

    def get_reputation(self):
        """
        Reputation determines the position of a post. This might be implemented in many ways,
        but for now it is simply upvotes - downvotes.
        """
        return self.n_upvotes - self.n_downvotes

    @property
    def n_comments(self):
        if self._n_comments is not None:
            return self._n_comments
        return self.get_tree_size() - 1

    @property
    def n_upvotes(self):
        if self._n_upvotes is not None:
            return self._n_upvotes
        return self.votes.filter(vote__gt=0).aggregate(n=Sum("vote"))["n"] or 0

    @property
    def n_downvotes(self):
        if self._n_downvotes is not None:
            return self._n_downvotes
        return -(self.votes.filter(vote__lt=0).aggregate(n=Sum("vote"))["n"] or 0)

    @property
    def cached(self):
        return self._reviews_children is not None

    @property
    def deleted(self):
        return self.text is None

    def cache(self, select_related=None, defer=None, order=False, order_reverse=False):
        """
        Caches all reviews in the complete review tree of self.paper. After calling the
        following properties are available (discouraged to use outside of this class):

           _reviews: a { review_id: Review(id=review_id) } mapping
           _reviews_children: a { review_id : [Review(parent_id=review_id)] } mapping



        @param select_related: fields to preselect (see Django select_related()). Called
                               on Review. Keep in mind that the properties `parent` and
                               `paper` will always be cached.
        @type select_related: list, tuple

        @param defer: fields to defer (see Django defer()). Called on Review.
        @type defer: list, tuple

        @param order: order cache and output of various commands according to get_reputation()
        @type order: bool

        @param order_reverse: reverse ordering (default ordering is descending)
        @type order_reverse: bool
        """
        if self.cached: return

        # Select review objects in complete tree
        reviews = self.paper.reviews.all()
        if select_related:
            reviews = reviews.select_related(*select_related)
        if defer:
            reviews = reviews.defer(*defer)

        if order:
            # Fallback ordering if reputation is equal
            reviews = reviews.order_by("id")
            reviews = sorted(reviews, key=lambda r: r.get_reputation(), reverse=not order_reverse)
            reviews = OrderedDict((r.id, r) for r in reviews)
        else:
            reviews = {r.id: r for r in reviews}

        self._reviews = reviews
        _self = reviews[self.id]
        self._reviews[self.id] = self

        # We need to set al select_related / defer caches on this object
        for prop in select_related or ():
            setattr(self, "_%s_cache" % prop, getattr(_self, prop))
        for prop in REVIEW_FIELDS - set(defer or ()):
            setattr(self, prop, getattr(_self, prop))

        # We want to create a review_id -> [children] mapping. After caching
        # each Review object in the cache shares the cache.
        mapping = defaultdict(list)
        paper = self.paper

        for review in self._reviews.values():
            mapping[review.parent_id].append(review)
            review._reviews = reviews
            review._reviews_children = mapping
            review._paper_cache = paper
            review._parent_cache = reviews.get(review.parent_id, None)

    def _get_tree(self, level, seen, lazy):
        if self.id in seen:
            # We've detected a loop. This should not happen, ever. Determine products
            # of the loop and raise a descriptive ValueError.
            seen, review = [], self
            while review.id not in seen:
                seen.append(review.id)
                review = review.parent

            # Add first one for nice error message
            seen.append(seen[0])

            raise ValueError("Detected loop: %s" % " -> ".join(map(str, seen)))

        seen.add(self.id)
        children = (r._get_tree(level=level+1, seen=seen, lazy=lazy) for r in self._reviews_children[self.id])
        return ReviewTree(review=self, level=level, children=children if lazy else list(children))

    def get_tree(self, lazy=True):
        """Generates a tree based upon ReviewTree. Calls cache() if needed.

        @param lazy: determines whether children properties are generators or lists.
        @type lazy: bool"""
        self.cache()
        return self._get_tree(level=0, seen=set(), lazy=lazy)

    def get_tree_size(self):
        return 1 + sum(r.review.get_tree_size() for r in self.get_tree().children)

    class Meta:
        app_label = "main"

    def __str__(self):
        return "{self.id}, poster={self.poster}, paper={self.paper}, parent={self.parent.id}".format(self=self)

    def _invalidate_template_caches(self):
        cache.delete(make_template_fragment_key('review', [self.paper_id, self.id]))

    def delete(self, using=None):
        self.text = None
        self.poster = None
        self.rating = -1
        self.save(using=using)

    def save(self, *args, **kwargs):
        # Check whether the whole tree has the same paper.
        if self.parent_id is not None and self.parent.paper_id is not self.paper_id:
            raise ValueError("parent.paper ({self.parent.paper_id}) was not {self.paper_id}".format(self=self))

        # We need to clean template caches if this is an existing review
        if self.id is not None:
            self._invalidate_template_caches()

        # Note: we should probably also check for loops, but this makes saving very
        # inefficient. Instead, when generating trees this issue is detected.
        return super().save(*args, **kwargs)

class Vote(models.Model):
    vote = models.SmallIntegerField(db_index=True)
    review = models.ForeignKey(Review, related_name="votes")
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="votes")

    class Meta:
        app_label = "main"

        # You can only vote once on a review
        unique_together = (("review", "voter"),)

    def __str__(self):
        return "{self.voter} voted {self.vote} on {self.review}".format(self=self)

    def delete(self, using=None):
        self.review._invalidate_template_caches()
        super().delete(using=using)

    def save(self, *args, **kwargs):
        self.review._invalidate_template_caches()

        if self.vote == 0:
            raise ValueError("You cannot vote neutral.")
        return super().save(*args, **kwargs)
