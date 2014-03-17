from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def login_required(function=None, raise_exception=False, **kwargs):
    """
    Behaves the same as django.contrib.auth.decorators.login_required, but
    takes an optional argument 'raise_exception' which causes the decorator
    to raise a PermissionDenied if user is not logged in.
    """
    def logged_in(user):
        if user.is_anonymous():
            if raise_exception:
                raise PermissionDenied
            return False
        return True

    decorator = user_passes_test(logged_in, **kwargs)
    return decorator(function) if function else decorator
