from functools import partial
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from openreview.apps.accounts.models import User
from openreview.apps.main.models import Paper, Review, Vote, Author, Keyword, Category

__all__ = ["ModelViewMixin"]

MODEL_MAP = {
    "paper_id": Paper,
    "review_id": Review,
    "vote_id": Vote,
    "author_id": Author,
    "user_id": User,
    "keyword_id": Keyword,
    "category_id": Category
}

MODEL_ATTRIBUTES = {
    "paper", "review", "vote", "author", "user", "keyword", "category"
}

class ModelViewMixin(object):
    """
    Provides a way of easily fetching models through a property called 'objects'. It
    looks at URL kwargs and decides if the model is available. For every model type
    it provides two properties: {model} and get_{model}. Example:

    >>> class TestView(View, ModelViewMixin):
    >>>     def get(self):
    >>>         print(self.objects.paper)

    This would look at two things:

        1. Is a URL keyword argument 'paper_id' given?
        2. Does Paper(id=paper_id) exist?

    If not (1) a KeyError is raised. If not (2) a Http404 is raised, automatically
    generating a 404 page if not caught. If you want to use one of the query functions
    of Django, you can use get_{model}, like so:

    >>> class TestView(View, ModelViewMixin):
    >>>     def get(self):
    >>>         paper = self.objects.get_paper(lambda p: p.select_related("poster"))

    This object will be cached an retrieved if self.objects.paper is requested. Calling
    get_paper() again would cause the cache to be overridden.
    """
    def __init__(self, *args, **kwargs):
        self.objects = ObjectManager(self)
        super().__init__(*args, **kwargs)

class ModelSerializerMixin(object):
    def dispatch(self, *args, **kwargs):
        self.objects = ObjectManager(self)
        return super().dispatch(*args, **kwargs)

class ObjectManager(object):
    def __init__(self, view):
        self.view = view

    def __getattr__(self, item):
        # Call get_{item} if we know this model type.
        if item in MODEL_ATTRIBUTES:
            return getattr(self, "get_%s" % item)()

        # Create partial _get_object function if we know this model type.
        model_name = item[4:]
        if item.startswith("get_") and model_name in MODEL_ATTRIBUTES:
            return partial(self._get_object, name=model_name)

        # We don't know this model type.
        raise AttributeError("%r object has no attribute %r" % (self.__class__, item))

    def _get_object(self, preprocess_func=lambda q: q, name=None):
        model = MODEL_MAP.get("%s_id" % name)
        queryset = preprocess_func(model.objects)

        try:
            obj = queryset.get(id=self.view.kwargs["%s_id" % name])
        except ObjectDoesNotExist:
            raise Http404

        # Cache object for next call
        setattr(self, name, obj)
        return obj
