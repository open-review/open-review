from urllib.request import urlopen
from bs4 import BeautifulSoup


class ScrapeError(ValueError):
    pass


class PaperMetaScraper:

    def __init__(self):
        self.title = None
        self.abstract = None
        self.publisher = None
        self.publish_date = None
        self.urls = None
        self.authors = None
        self.keywords = None
        self.bs = None
    def parse(self,url):
        pass

    def get_results(self):
        return { "title": self.title,
                 "abstract": self.abstract,
                 "publisher": self.publisher,
                 "publish_date": self.publish_date,
                 "urls": self.urls,
                 "authors": self.authors,
                 "keywords": self.keywords}


class ArXivScraper(PaperMetaScraper):

    def parse(self,id):
        self.urls = "http://arxiv.org/abs/{id}".format(id=id)
        self.bs = BeautifulSoup(urlopen(self.urls))
        self.title = self.bs.select("div.leftcolumn h1.title")[0].span.nextSibling
        #I need a functional language
        self.authors = list(map(lambda x: x.text, self.bs.select("div.leftcolumn div.authors a")))
        self.abstract = self.bs.select("blockquote.abstract span")[0].nextSibling
        return self