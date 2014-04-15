import datetime

from django.utils import timezone
from django.db import models
from django.db.models import Count

from openreview.apps.main.models.category import Category
from openreview.apps.main.models.review import Vote, Review
from openreview.apps.main.models.author import Author


__all__ = ["Keyword", "Paper", "Category"]


class Keyword(models.Model):
    label = models.TextField(db_index=True)

    def __str__(self):
        return self.label

    class Meta:
        app_label = "main"


class Paper(models.Model):
    doc_id = models.TextField(verbose_name="document identifier", null=True)
    title = models.TextField()
    abstract = models.TextField()
    publisher = models.TextField(null=True, blank=True)
    publish_date = models.DateField(null=True, blank=True)
    urls = models.TextField(null=True, blank=True)

    # These fields are *probably* a bad idea performance wise.
    authors = models.ManyToManyField(Author)
    keywords = models.ManyToManyField(Keyword)
    categories = models.ManyToManyField(Category, blank=True)    

    @classmethod
    def trending(cls, top=5, days=7):
        """Returns the trending papers. The paper with the most reviews the last
        seven days will end on top. Papers without (recent) reviews cannot be trending.

        @param top: return the top N papers
        @type top: int

        @rtype: list
        """
        seven_days_ago = timezone.now() - datetime.timedelta(days=days)
        reviews = Review.objects.filter(parent__isnull=True, timestamp__gt=seven_days_ago)
        papers = reviews.values_list('paper').annotate(n=Count('paper')).order_by("-n")[0:top]
        papers_objects = Paper.objects.in_bulk(pid for pid, pcount in papers)
        return [papers_objects[pid] for pid, pcount in papers]

    @classmethod
    def latest(cls):
        return Paper.objects.order_by('-publish_date')

    @classmethod
    def controversial(cls, top=5, days=7):
        """Returns list of the most controversial papers.

        TODO: Implement ;-)
        """
        seven_days_ago = timezone.now() - datetime.timedelta(days=days)
        reviews = Review.objects.filter(parent__isnull=True, timestamp__gt=seven_days_ago)
        return Paper.objects.order_by()

    def get_reviews(self):
        return self.reviews.filter(parent__isnull=True)

    def get_comments(self):
        return self.reviews.filter(parent__isnull=False)

    def num_reviews(self):
        return self.get_reviews().count()

    def get_votes(self, include_comments):
        """
        Returns votes, which gives a rough indicator of its popularity.

        @param include_comments: include reviews with parent != None.
        @type include_comments: bool

        @rtype: QuerySet(Review)
        """
        votes = Vote.objects.filter(review__paper=self)
        return votes if include_comments else votes.filter(parent=None)

    def __str__(self):
        return self.title

    class Meta:
        app_label = "main"
