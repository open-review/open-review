"""
This module contains convenience functions for testing purposes.
"""
from functools import wraps
from django.conf import settings
from django.test import LiveServerTestCase
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from datetime import datetime

# Determine the WebDriver module. Defaults to Firefox.
from openreview.apps.accounts.models import User
from openreview.apps.main.models import Author, Paper, Keyword, Review, Vote

try:
    web_driver_module = settings.SELENIUM_WEBDRIVER
except AttributeError:
    from selenium.webdriver.firefox import webdriver as web_driver_module

class SeleniumWebDriver(web_driver_module.WebDriver):
    """Default webdriver, extended with convenience methods."""

    def find_css(self, css_selector):
        """Shortcut to find elements by CSS. Returns either a list or singleton"""
        elems = self.find_elements_by_css_selector(css_selector)
        found = len(elems)
        if found == 1:
            return elems[0]
        elif not elems:
            raise NoSuchElementException(css_selector)
        return elems

    def wait_for_css(self, css_selector, timeout=7):
        """Shortcut for WebDriverWait"""
        try:
            return WebDriverWait(self, timeout).until(lambda driver: driver.find_css(css_selector))
        except TimeoutException:
            self.quit()


class SeleniumTestCase(LiveServerTestCase):
    """TestCase for in-browser testing. Sets up `wd` property, which is an initialised Selenium
    webdriver (defaults to Firefox)."""

    def open(self, url):
        self.wd.get("%s%s" % (self.live_server_url, url))

    def setUp(self):
        self.wd = SeleniumWebDriver()
        super().setUp()

    def tearDown(self):
        self.wd.quit()
        super().tearDown()

# This is a hack to generate unique names for test models
COUNTER = 0
def up_counter(func):
    @wraps(func)
    def inner(*args, **kwargs):
        global COUNTER
        COUNTER += 1
        return func(*args, **kwargs)
    return inner

@up_counter
def create_test_user(**kwargs):
    return User.objects.create_user(**dict({
        "username": "user-%s" % COUNTER,
        "password": "test"
    }, **kwargs))

@up_counter
def create_test_author(**kwargs):
    return Author.objects.create(**dict({"name": "author-%s" % COUNTER}, **kwargs))

@up_counter
def create_test_keyword(label="keyword - %s"):
    return Keyword.objects.create(label=label % COUNTER)

@up_counter
def create_test_paper(n_authors=0, n_keywords=0, n_comments=0, n_reviews=0, **kwargs):
    paper = Paper.objects.create(**dict({"title": "paper-%s" % COUNTER, "abstract": "abstract"}, **kwargs))

    if n_authors > 0:
        for i in range(n_authors):
            paper.authors.add(create_test_author())

    if n_keywords > 0:
        for i in range(n_keywords):
            paper.keywords.add(create_test_keyword())

    if n_reviews > 0:
        for i in range(n_reviews):
            create_test_review(paper=paper)

    if n_comments > 0:
        if paper.reviews.count() == 0:
            create_test_review(paper=paper)

        review = paper.reviews.all()[0]
        for i in range(n_comments):
            create_test_review(parent=review, paper=paper)

    return paper

@up_counter
def create_test_review(**kwargs):
    paper, poster = None, None
    if "paper" not in kwargs:
        paper = create_test_paper()
    if "poster" not in kwargs:
        poster = create_test_user()
    
    return Review.objects.create(**dict({
        "text": "review content",
        "poster": poster,
        "paper": paper,
        "timestamp": datetime.now()
    }, **kwargs))

def add_test_vote(paper, vote):
    if paper.num_reviews() == 0:
        create_test_review(paper=paper)
    
    review = paper.get_reviews()[0]
    vote = Vote.objects.create(**dict({
    	"vote" : vote,
    	"review" : review,
    	"voter" : review.poster
    }))
