from haystack import indexes
from .models.paper import Paper, Author


class PaperIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='title')
    content_auto = indexes.EdgeNgramField(model_attr='title')

    def get_model(self):
        return Paper


class AuthorIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='name')

    def get_model(self):
        return Author
