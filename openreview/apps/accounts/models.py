from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Copies properties of default User model. Defining it ourselves
    adds the ability to add/change properties later on without too much
    hassle."""