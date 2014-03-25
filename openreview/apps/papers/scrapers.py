from django.core.cache import cache

from openreview.apps.main.models.paper import Paper

from urllib.request import urlopen
import lxml.html
from collections import defaultdict
from datetime import datetime


class PaperMetaScraper:

    class ScrapingError(BaseException):
        def __str__(self):
            return "An error has occured during scraping"

    def __init__(self, caching=True):
        self.fields = defaultdict()
        self.parser = None
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
                self.parser = lxml.html.parse(urlopen(("http://export.arxiv.org/api/query?search_query=id:{id}" +
                                                      "&start=0&max_results=1").format(id=doc_id))).getroot()
                self.fields['title'] = self.parser.cssselect("entry title")[0].text
                self.fields['abstract'] = self.parser.cssselect("entry summary")[0].text
                self.fields['authors'] = [x.text for x in self.parser.cssselect("entry author name")]
                # self.fields['published'] = datetime.strptime(self.parser.cssselect("entry published")[0].text,"%Y-%m-%dT%H:%M:%SZ")

                if self.caching:
                    cache.set("arxiv-res-{id}".format(id=doc_id), self.fields)
            except Exception:
                raise PaperMetaScraper.ScrapingError()
        return self