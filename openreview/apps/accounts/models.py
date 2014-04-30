from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Copies properties of default User model. Defining it ourselves
    adds the ability to add/change properties later on without too much
    hassle."""
    title = models.CharField(max_length=20, null=True, blank=True)
    university = models.CharField(max_length=100, null=True, blank=True)