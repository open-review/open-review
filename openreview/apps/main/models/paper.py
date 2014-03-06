import datetime
from django.db import models
from django.db.models import Count
import operator

from openreview.apps.main.models.review import Vote, Review
from openreview.apps.main.models.author import Author


__all__ = ["Keyword", "Paper"]


class Keyword(models.Model):
    label = models.TextField()

    def __str__(self):
        return self.label

    class Meta:
        app_label = "main"


class Paper(models.Model):
    doc_id = models.TextField(help_text="Identifier: can either be a real DOI or a domain-specific one. "
                                        "For example: arXiv:1403.0438.", null=True)
    title = models.TextField()
    abstract = models.TextField()
    publisher = models.TextField(null=True, blank=True)
    publish_date = models.DateField(null=True)
    urls = models.TextField(null=True, blank=True)

    # These fields are *probably* a bad idea performance wise.
    authors = models.ManyToManyField(Author)
    keywords = models.ManyToManyField(Keyword)

    def get_reviews(self):
        return self.reviews.filter(parent__isnull=True)

    def num_reviews(self):
        return len(self.get_reviews())

    @classmethod
    def trending(cls, top=5):
        """Returns the trending papers. The paper with the most reviews the last
        seven days will end on top. Papers without (recent) reviews cannot be trending.

        @param top: return the top N papers
        @type top: int

        @rtype: list
        """
        seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        reviews = Review.objects.filter(parent__isnull=True, timestamp__gt=seven_days_ago)
        papers = reviews.values('paper').annotate(n=Count('paper')).order_by("-n")[0:top]
        papers_ids = tuple(map(operator.itemgetter("paper"), papers))

        # Papers may be returned in any order by de db, but we need it in the order
        # specified in paper_ids, sorted() solves this. This might be inefficient for
        # large values of `top`, as index complexity is O(n).
        papers = Paper.objects.filter(id__in=papers_ids)
        return sorted(papers, key=lambda p: papers_ids.index(p.id))

    @classmethod
    def latest(cls):
        return Paper.objects.order_by('-publish_date')

    @classmethod
    def controversial(cls, top=5):
        """Returns list of the most controversial papers.

        TODO: Implement ;-)
        """
        return Paper.objects.order_by()

    def get_comments(self):
        return self.reviews.filter(parent__isnull=False)

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
