from itertools import chain
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import HyperlinkedModelSerializer
from openreview.apps.api.fields import CustomHyperlinkedRelatedField


class CustomHyperlinkedModelSerializer(HyperlinkedModelSerializer):
    _hyperlink_field_class = CustomHyperlinkedRelatedField

    @property
    def request(self):
        # Another hack: add property request, as we often need to access the currently
        # logged in user.
        return self.context["view"].request

    def get_pk_field(self, model_field):
        # HyperlinkedModelSerializer hides the 'id' field by default, and gives no
        # option to disable it gracefully. This patches it so it will display these
        # fields.
        return self.get_field(model_field)

    def save_object(self, obj, **kwargs):
        # save() functions can raise ValueErrors, which contents are displayed when
        # returning an error (with a HTTP403)
        try:
            return super().save_object(obj, **kwargs)
        except ValueError as e:
            raise PermissionDenied(str(e))
