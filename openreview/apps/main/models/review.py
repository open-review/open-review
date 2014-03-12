from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum

__all__ = ["Review", "Vote", "set_n_votes_cache"]

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

    class Meta:
        app_label = "main"

    def __str__(self):
        return "Review: {self.poster}, {self.paper}, {self.parent}".format(self=self)


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
