from django.core.cache import cache

from openreview.apps.main.models.paper import Paper

from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import defaultdict


class PaperMetaScraper:

    class ScrapingError(BaseException):
        def __str__(self):
            return "An error has occured during scraping"

    def __init__(self, caching=True):
        self.fields = defaultdict()
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
            try:
                self.fields['doc_id'] = doc_id
                self.fields['urls'] = "http://arxiv.org/abs/{id}".format(id=doc_id)
                self.bs = BeautifulSoup(urlopen(self.fields['urls']))
                self.fields['title'] = self.bs.select("div.leftcolumn h1.title")[0].span.nextSibling
                self.fields['authors'] = [x.text for x in self.bs.select("div.leftcolumn div.authors a")]
                self.fields['abstract'] = self.bs.select("blockquote.abstract span")[0].nextSibling
                if self.caching:
                    cache.set("arxiv-res-{id}".format(id=doc_id), self.fields)
            except Exception:
                raise PaperMetaScraper.ScrapingError()
        return self