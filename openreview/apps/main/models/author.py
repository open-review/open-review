from django.db import models
from django.conf import settings

__all__ = ["Author"]


class Author(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="authors")
    name = models.TextField(unique=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "main"
