from django.core.exceptions import ObjectDoesNotExist
from rest_framework.fields import Field
from rest_framework.relations import HyperlinkedRelatedField


class RelativeField(Field):
    def field_to_native(self, obj, field_name):
        url_field = self.parent.fields['url']
        view_name = url_field.view_name
        url = url_field.get_url(obj, view_name, self.parent.request, None)
        return "{url}{field_name}/".format(**locals())


class CustomHyperlinkedRelatedField(HyperlinkedRelatedField):
    """
    Patched version of `rest_framework.fields.HyperlinkedRelatedField`: also accepts
    primary keys (along urls) when parsing.
    """
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
