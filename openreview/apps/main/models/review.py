from collections import namedtuple, collections
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum

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
    text = models.TextField(verbose_name="contents")
    rating = models.SmallIntegerField(default=-1)
    timestamp = models.DateTimeField(auto_now_add=True)

    poster = models.ForeignKey(get_user_model())
    paper = models.ForeignKey("main.Paper", related_name="reviews")
    parent = models.ForeignKey("self", null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._n_upvotes = None
        self._n_downvotes = None

        # If cache() is called this is a defaultdict(list) with
        # review_id -> [children_ids].
        self._reviews_children = None

        # If cache() is called, this contains a review_id -> Review mapping
        self._reviews = None

    @property
    def comments(self):
        return Review.objects.filter(paper__id=self.paper_id, parent__isnull=False)

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

    def cache(self, select_related=None, defer=None):
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
        """
        if self.cached: return

        # Select review objects in complete tree
        reviews = self.paper.reviews.all()
        if select_related:
            reviews = reviews.select_related(*select_related)
        if defer:
            reviews = reviews.defer(*defer)

        self._reviews = _reviews = {r.id: r for r in reviews}
        _self = _reviews[self.id]
        self._reviews[self.id] = self

        # We need to set al select_related / defer caches on this object
        for prop in select_related or ():
            setattr(self, "_%s_cache" % prop, getattr(_self, prop))
        for prop in REVIEW_FIELDS - set(defer or ()):
            setattr(self, prop, getattr(_self, prop))

        # We want to create a review_id -> [children] mapping. After caching
        # each Review object in the cache shares the cache.
        mapping = collections.defaultdict(list)
        paper = self.paper

        for review in _reviews.values():
            mapping[review.parent_id].append(review)
            review._reviews = _reviews
            review._reviews_children = mapping
            review._paper_cache = paper
            review._parent_cache = _reviews.get(review.parent_id, None)

    def _get_tree(self, level, seen):
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
        children = [r._get_tree(level=level+1, seen=seen) for r in self._reviews_children[self.id]]
        return ReviewTree(review=self, level=level, children=children)

    def get_tree(self):
        """Generates a tree based upon ReviewTree. Calls cache() if needed."""
        self.cache()
        return self._get_tree(level=0, seen=set())

    class Meta:
        app_label = "main"

    def __str__(self):
        return "Review: {self.poster}, {self.paper}, {self.parent}".format(self=self)

    def save(self, *args, **kwargs):
        # Check whether the whole tree has the same paper.
        if self.parent_id is not None and self.parent.paper_id is not self.paper_id:
            raise ValueError("parent.paper ({self.parent.paper_id}) was not {self.paper_id}".format(self=self))

        # Note: we should probably also check for loops, but this makes saving very
        # inefficient. Instead, when generating trees this issue is detected.
        return super().save(*args, **kwargs)

class Vote(models.Model):
    vote = models.SmallIntegerField(db_index=True)
    review = models.ForeignKey(Review, related_name="votes")
    voter = models.ForeignKey(get_user_model(), related_name="votes")

    class Meta:
        app_label = "main"

        # You can only vote once on a review
        unique_together = (("review", "voter"),)

    def __str__(self):
        return "{self.voter} voted {self.vote} on {self.review}".format(self=self)

    def save(self, *args, **kwargs):
        if self.vote == 0:
            raise ValueError("You cannot vote neutral.")
        return super().save(*args, **kwargs)
