from django.contrib.auth import get_user_model
from django.db import models

__all__ = ["Review", "Vote"]


class Review(models.Model):
    """
    A review can either be a 'real' review of a paper (parent == None) or a meta-review, which is
    referred to as a comment in the user interface (parent != None).
    """
    text = models.TextField(verbose_name="contents")
    timestamp = models.DateTimeField(auto_now_add=True)

    poster = models.ForeignKey(get_user_model())
    paper = models.ForeignKey("main.Paper", related_name="reviews")
    parent = models.ForeignKey("self", null=True)

    class Meta:
        app_label = "main"

    def __str__(self):
        return "Review: {self.poster}, {self.paper}, {self.parent}".format(self=self)


class Vote(models.Model):
    vote = models.SmallIntegerField()
    review = models.ForeignKey(Review)
    voter = models.ForeignKey(get_user_model())

    class Meta:
        app_label = "main"
