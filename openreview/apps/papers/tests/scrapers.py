import unittest
import os

from openreview.apps.papers import scrapers
from openreview.apps.main.models import Category
from django.core import management

__all__ = ['TestArXivScraper']


class TestArXivScraper(unittest.TestCase):
    def setUp(self):
        self.arxivscraper = scrapers.Controller(scrapers.ArXivScraper, caching=False)
        self.oldurlopen = scrapers.urlopen
        scrapers.urlopen = lambda x: open(os.path.dirname(os.path.realpath(__file__)) +
                                          "/../testfiles/1306.3879.xml")

    def tearDown(self):
        scrapers.urlopen = self.oldurlopen

    def test_arxiv_scraper(self):
        results = self.arxivscraper.run("1306.3879")
        self.assertEqual(results['title'], """Chandra View of the Ultra-Steep Spectrum Radio Source in Abell 2443:
  Merger Shock-Induced Compression of Fossil Radio Plasma?""")
        self.assertEqual(results['authors'], ["T. E. Clarke", "S. W. Randall", "C. L. Sarazin",
                                              "E. L. Blanton", "S. Giacintucci"])
        self.assertEqual(results['abstract'],
                         """  We present a new Chandra X-ray observation of the intracluster medium in the
galaxy cluster Abell 2443, hosting an ultra-steep spectrum radio source. The
data reveal that the intracluster medium is highly disturbed. The thermal gas
in the core is elongated along a northwest to southeast axis and there is a
cool tail to the north. We also detect two X-ray surface brightness edges near
the cluster core. The edges appear to be consistent with an inner cold front to
the northeast of the core and an outer shock front to the southeast of the
core. The southeastern edge is coincident with the location of the radio relic
as expected for shock (re)acceleration or adiabatic compression of fossil
relativistic electrons.\n""")
        self.assertEqual(results['doc_id'], "1306.3879")
        self.assertEqual(results['urls'], "http://arxiv.org/abs/1306.3879v1")
        self.assertEqual(results['categories'], [Category.objects.get(arxiv_code='astro-ph.CO').pk])
