from django.core.cache import cache

from openreview.apps.main.models.paper import Paper

from urllib.request import urlopen
from bs4 import BeautifulSoup


class PaperMetaScraper:

    def __init__(self, caching=True):
        self.fields = {
            "doc_id": None,
            "title":  None,
            "abstract": None,
            "publisher": None,
            "publish_date": None,
            "urls": None,
            "authors": None,
            "keywords": None}
        self.bs = None
        self.caching = caching

    def parse(self, url):
        pass

    def get_results(self):
        return self.fields

    def results_as_model_object(self):
        return Paper(self.fields)


class ArXivScraper(PaperMetaScraper):

    def parse(self, doc_id):
        if self.caching and cache.get("arxiv-res-{id}".format(id=doc_id)):
            self.fields = cache.get("arxiv-res-{id}".format(id=doc_id))
        else:
            self.fields['id'] = doc_id
            self.fields['urls'] = "http://arxiv.org/abs/{id}".format(id=doc_id)
            self.bs = BeautifulSoup(urlopen(self.fields['urls']))
            self.fields['title'] = self.bs.select("div.leftcolumn h1.title")[0].span.nextSibling
            #I need a functional language
            self.fields['authors'] = list(map(lambda x: x.text, self.bs.select("div.leftcolumn div.authors a")))
            self.fields['abstract'] = self.bs.select("blockquote.abstract span")[0].nextSibling
            if self.caching:
                cache.set("arxiv-res-{id}".format(id=doc_id), self.fields)
        return self