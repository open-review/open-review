from rest_framework.permissions import BasePermission


class ObjectPermissions(BasePermission):
    """
    Tests methods can_delete and can_change of model instances. This permission class
    can be applied to views defining either `queryset` or `model`.
    """
    # If we can't find a function on given instance, we return..
    default = False

    # HTTP method to can_* mapping
    perm_map = {
        "PATCH": "change",
        "PUT": "change",
        "DELETE": "delete"
    }

    def has_object_permission(self, request, view, obj):
        try:
            test_func = getattr(obj, "can_%s" % self.perm_map[request.method])
        except AttributeError:
            return self.default
        except KeyError:
            # We don't consider methods beside PATCH / PUT / DELETE
            return True

        return test_func(request.user)
