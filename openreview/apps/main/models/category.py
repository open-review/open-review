from django.db import models

__all__ = ["Category"]

class Category(models.Model):
    name = models.TextField()
    arxiv_code = models.TextField(null=True, unique=True)
    parent = models.ForeignKey("main.Category", null=True, related_name="children")

    def __str__(self):
        return self.name

    class Meta:
        app_label = "main"
