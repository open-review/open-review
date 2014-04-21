from django.db import models

__all__ = ["Category"]

class Category(models.Model):
    name = models.TextField()
    arxiv_code = models.TextField(null=True, unique=True)
    parent = models.ForeignKey("main.Category", null=True, related_name="children")

    @property
    def papers(self):
        # Prevent circular imports
        from openreview.apps.main.models import Paper
        return Paper.objects.filter(categories__id=self.id)

    def save(self, test_environment=False, **kwargs):
        if not test_environment:
            raise ValueError("Categories cannot be 'dynamically' added.")
        return super().save(**kwargs)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "main"
