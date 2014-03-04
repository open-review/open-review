from django.db import models
from openreview.apps.main.models.author import Author

__all__ = ["Keyword", "Paper"]


class Keyword(models.Model):
    label = models.TextField()

    def __str__(self):
        return self.label

    class Meta:
        app_label = "main"


class URL(models.Model):
    url = models.TextField()
    title = models.TextField(null=True)

    class Meta:
        app_label = "main"


class Paper(models.Model):
    doc_id = models.TextField(help_text="Identifier: can either be a real DOI or a domain-specific one. "
                                        "For example: arXiv:1403.0438.", null=True)
    title = models.TextField()
    abstract = models.TextField()
    publisher = models.TextField(null=True)
    publish_date = models.DateField(null=True)

    # These fields are *probably* a bad idea performance wise.
    authors = models.ManyToManyField(Author)
    keywords = models.ManyToManyField(Keyword)
    urls = models.ManyToManyField(URL)

    def get_reviews(self):
        return self.reviews.filter(parent__isnull=True)

    def get_comments(self):
        return self.reviews.filter(parent__isnull=False)

    def __str__(self):
        return self.title

    class Meta:
        app_label = "main"