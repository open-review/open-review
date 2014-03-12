from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum

__all__ = ["Review", "Vote"]


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

    @property
    def comments(self):
        return Review.objects.filter(paper__id=self.paper_id, parent__isnull=False)

    @property
    def n_upvotes(self):
        return self.votes.filter(vote__gt=0).aggregate(n=Sum("vote"))["n"] or 0

    @property
    def n_downvotes(self):
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
