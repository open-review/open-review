import json

import os
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core import management
from openreview.apps.papers import scrapers
from openreview.apps.tools.testing import BaseTestCase
from openreview.apps.main.models import Category


__all__ = ['TestArXivScraper']


class TestArXivScraper(BaseTestCase):
    expected_title = """Chandra View of the Ultra-Steep Spectrum Radio Source in Abell 2443:
  Merger Shock-Induced Compression of Fossil Radio Plasma?"""
    expected_authors = ["T. E. Clarke", "S. W. Randall", "C. L. Sarazin",
                        "E. L. Blanton", "S. Giacintucci"]
    expected_abstract = """  We present a new Chandra X-ray observation of the intracluster medium in the
galaxy cluster Abell 2443, hosting an ultra-steep spectrum radio source. The
data reveal that the intracluster medium is highly disturbed. The thermal gas
in the core is elongated along a northwest to southeast axis and there is a
cool tail to the north. We also detect two X-ray surface brightness edges near
the cluster core. The edges appear to be consistent with an inner cold front to
the northeast of the core and an outer shock front to the southeast of the
core. The southeastern edge is coincident with the location of the radio relic
as expected for shock (re)acceleration or adiabatic compression of fossil
relativistic electrons.\n"""
    expected_doc_id = "1306.3879"
    expected_urls = "http://arxiv.org/abs/1306.3879v1"
    expected_categories = Category.objects.filter(arxiv_code='astro-ph.CO').values_list("id", flat=True)

    def setUp(self):
        management.call_command("loaddata", "categories", verbosity=0)
        self.arxivscraper = scrapers.Controller(scrapers.ArXivScraper, caching=False)
        self.oldurlopen = scrapers.urlopen
        scrapers.urlopen = lambda x: open(os.path.dirname(os.path.realpath(__file__)) +
                                          "/../fixtures/arxiv/1306.3879.xml")

    def tearDown(self):
        scrapers.urlopen = self.oldurlopen

    def test_arxiv_scraper(self):
        results = self.arxivscraper.run("1306.3879")
        self.assertEqual(results['title'], self.expected_title)
        self.assertEqual(results['authors'], self.expected_authors)
        self.assertEqual(results['abstract'], self.expected_abstract)
        self.assertEqual(results['doc_id'], self.expected_doc_id)
        self.assertEqual(results['urls'], self.expected_urls)
        self.assertEqual(results['categories'], list(self.expected_categories))

    def test_arxiv_scraper_request(self):
        response = Client().get(reverse("arxiv-scraper", kwargs={'doc_id': "1306.3879"}))
        result = json.loads(response.content.decode("utf-8"))
        self.assertEqual(result.get('title'), self.expected_title)
        self.assertEqual(result.get('authors'), self.expected_authors)
        self.assertEqual(result.get('abstract'), self.expected_abstract)
        self.assertEqual(result.get('doc_id'), self.expected_doc_id)
        self.assertEqual(result.get('urls'), self.expected_urls)
        self.assertEqual(result.get('categories'), list(self.expected_categories))
