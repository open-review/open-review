from django.contrib.auth import get_user_model
from django.db import models

__all__ = ["Author"]


class Author(models.Model):
    user = models.ForeignKey(get_user_model(), null=True)
    name = models.TextField(unique=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "main"
