from django.contrib.auth.models import AbstractUser
from openreview.apps.main.models.review import bulk_delete
from django.db import models


class User(AbstractUser):
    """Copies properties of default User model. Defining it ourselves
    adds the ability to add/change properties later on without too much
    hassle."""
    votes_public = models.BooleanField(default=False)

    def delete(self, delete_reviews=False):
        if delete_reviews:
            bulk_delete(self.reviews.all())
        else:
            self.reviews.all().update(poster=None, anonymous=True)
        super().delete()

