from django.contrib.auth import get_user_model
from django.db import models

__all__ = ["Author"]


class Author(models.Model):
    user = models.ForeignKey(get_user_model(), null=True)
    name = models.TextField(unique=True)

    class Meta:
        app_label = "main"
