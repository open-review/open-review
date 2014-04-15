from django.core.cache import cache

from urllib.request import urlopen, HTTPError
from datetime import datetime
from openreview.apps.main.models import Category

import lxml.html
import lxml.etree


class ScraperError(BaseException):
        pass


class Controller:
    def __init__(self, scraper, caching=True):
        self.scraper = scraper
        self.scraper_name = scraper.__class__.__name__
        self.caching = caching

    def run(self, doc_id):
        url = self.scraper.get_url(doc_id)

        if self.caching and cache.get("{scraper}-res-{id}".format(scraper=self.scraper_name, id=doc_id)):
            return cache.get("{scraper}-res-{id}".format(scraper=self.scraper_name, id=doc_id))
        else:
            try:
                doc = self.scraper.get_doc(url)
            except self.scraper.fetching_errors:
                raise ScraperError("An exception occurred while fetching {doc_id}".format(**locals()))

            try:
                result = dict(self.scraper.parse(doc))
            except self.scraper.parsing_errors:
                raise ScraperError("An exception occurred while parsing {doc_id}".format(**locals()))

            result.update({"doc_id": doc_id})

            if self.caching:
                cache.set("{scraper}-res-{id}".format(scraper=self.scraper_name, id=doc_id), result)
            return result


class Scraper:
    scarper_url = None
    parser = lxml.html.parse

    fetching_errors = HTTPError
    parsing_errors = (lxml.etree.LxmlError, IndexError)

    @classmethod
    def get_url(cls, doc_id):
        return cls.scraper_url.format(doc_id=doc_id)

    @classmethod
    def get_doc(cls, url):
        return cls.parser(urlopen(url)).getroot()

    @classmethod
    def parse(cls, doc):
        raise NotImplemented


class ArXivScraper(Scraper):
    scraper_url = "http://export.arxiv.org/api/query?search_query=id:{doc_id}&start=0&max_results=1"

    @classmethod
    def parse(cls, doc):
        yield "urls", doc.cssselect("entry id")[0].text
        yield "title", doc.cssselect("entry title")[0].text
        yield "abstract", doc.cssselect("entry summary")[0].text
        yield "authors", [x.text for x in doc.cssselect("entry author name")]
        yield "publisher", "ArXiv"
        yield "publish_date", datetime.strptime(doc.cssselect("entry published")[0].text, "%Y-%m-%dT%H:%M:%SZ")
        yield "categories", [c.pk for c in Category.objects.filter(arxiv_code__in=[x.get('term') for x in doc.cssselect("entry category")])]
