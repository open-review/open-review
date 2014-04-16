from rest_framework.serializers import HyperlinkedModelSerializer

# HyperlinkedModelSerializer hides the 'id' field by default, and gives no
# option to disable it gracefully. This patches it so it will display these
# fields.
def get_pk_field(self, model_field):
    return self.get_field(model_field)

# Another hack: add property request, as we often need to access the currently
# logged in user.
@property
def request(self):
    return self.context["view"].request

HyperlinkedModelSerializer.get_pk_field = get_pk_field
HyperlinkedModelSerializer.request = request
