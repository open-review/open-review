import unittest
import os

from openreview.apps.papers.scrapers import ArXivScraper


class TestArXivScraper(unittest.TestCase):
    def setUp(self):
        self.arxivscraper = ArXivScraper(caching=False)
        self.arxivscraper.urlopen = lambda x: open(os.path.dirname(os.path.realpath(__file__)) +
                                                   "/testfiles/1306.3879.html")

    def test_arxiv_scraper(self):
        results = self.arxivscraper.parse("1306.3879").get_results()
        self.assertEqual(results['title'], "\nChandra View of the Ultra-Steep Spectrum Radio Source in Abell 2443:"+
                                           "  Merger Shock-Induced Compression of Fossil Radio Plasma?")
        self.assertEqual(results['authors'], ["T. E. Clarke", "S. W. Randall", "C. L. Sarazin",
                                              "E. L. Blanton", "S. Giacintucci"])
        self.assertEqual(results['abstract'],
                         """ We present a new Chandra X-ray observation of the intracluster medium in the
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
        self.assertEqual(results['urls'], "http://arxiv.org/abs/1306.3879")
