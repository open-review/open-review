from django.contrib.auth.models import AbstractUser
from openreview.apps.main.models.review import bulk_delete


class User(AbstractUser):
    """Copies properties of default User model. Defining it ourselves
    adds the ability to add/change properties later on without too much
    hassle."""

    def delete(self, delete_reviews=False):
        if delete_reviews:
            bulk_delete(self.reviews.all())
        else:
            self.reviews.all().update(poster=None, anonymous=True)
        super().delete()