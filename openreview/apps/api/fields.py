from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework.exceptions import APIException
from rest_framework.fields import Field
from rest_framework.relations import HyperlinkedRelatedField, HyperlinkedIdentityField
from openreview.apps.tools.string import to_bool


class RelativeField(Field):
    def field_to_native(self, obj, field_name):
        url_field = self.parent.fields['url']
        view_name = url_field.view_name
        url = url_field.get_url(obj, view_name, self.parent.request, None)
        return "{url}{field_name}/".format(**locals())

def show_hyperlinks(request):
    hyperlinks = request.GET.get("hyperlinks", True)

    try:
        hyperlinks = to_bool(hyperlinks)
    except ValueError:
        raise APIException("GET parameter hyperlinks (=> {hyperlinks}) is not a valid boolean.".format(**locals()))

    return hyperlinks


class CustomHyperlinkedRelatedField(HyperlinkedRelatedField):
    """
    Patched version of `rest_framework.fields.HyperlinkedRelatedField`: also accepts
    primary keys (along urls) when parsing.
    """
    def to_native(self, obj):
        if not show_hyperlinks(self.context["request"]):
            return obj.id
        return super().to_native(obj)

    def from_native(self, value):
        try:
            pk = int(value)
        except ValueError:
            return super().from_native(value)

        # Could be a primary key value, try to fetch object. If it fails, pass judgement
        # to parent.
        try:
            return self.queryset.get(pk=pk)
        except ObjectDoesNotExist:
            return super().from_native(value)

class HyperlinkedRelatedFieldOrNone(CustomHyperlinkedRelatedField):
    def __init__(self, test=lambda o: True, **kwargs):
        self.test = test
        super().__init__(**kwargs)

    def field_to_native(self, obj, field_name):
        if self.test(self.parent.request.user, obj):
            return super().field_to_native(obj, field_name)
