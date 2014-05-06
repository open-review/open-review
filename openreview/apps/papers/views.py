from functools import partial
import json

from django.core.paginator import Paginator, EmptyPage
from django.http import Http404
from django.shortcuts import HttpResponse, redirect
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_page
from haystack.query import SearchQuerySet
from django.views.generic import TemplateView

from openreview.apps.main.models import set_n_votes_cache, Review, Vote, Paper, ReviewTree
from openreview.apps.tools.views import ModelViewMixin
from openreview.apps.papers import scrapers


class BaseReviewView(ModelViewMixin, TemplateView):
    def redirect(self, review):
        review.cache()

        # Determine root of comment thread
        root = review
        while root.parent is not None:
            root = root.parent

        url = reverse("review", args=[review.paper_id, root.id])
        return redirect("{url}#r{review.id}".format(**locals()), permanent=False)

    def get_context_data(self, **kwargs):
        # Do not load context data if user is anonymous (no posts) or
        # the current method is POST (votes/reviews not needed)
        if self.request.user.is_anonymous():
            return super().get_context_data(**kwargs)

        # Passing reviews and votes of user allows efficient caching of templates
        # as we gain the possibility to let javascript do the markup
        my_reviews = Review.objects.filter(paper=self.objects.paper, poster=self.request.user)
        my_reviews = tuple(my_reviews.values_list("id", flat=True))

        my_votes = Vote.objects.filter(review__paper=self.objects.paper, voter=self.request.user)
        my_votes = dict(my_votes.values_list("review__id", "vote"))

        return super().get_context_data(
            my_reviews=json.dumps(my_reviews),
            my_votes=json.dumps(my_votes),
            **kwargs
        )


class PaperWithReviewsView(BaseReviewView):
    template_name = "papers/paper.html"

    def get_context_data(self, **kwargs):
        paper = self.objects.get_paper(lambda p: p.prefetch_related("authors", "keywords", "categories"))

        try:
            review = paper.get_reviews()[0]
        except IndexError:
            reviews = []
        else:
            review.cache(select_related=["poster"])
            reviews = [r for r in review._reviews.values() if r.parent_id is None]

        # Set cache and sort reviews by up-/downvotes
        set_n_votes_cache(reviews)
        reviews.sort(key=lambda r: r.n_upvotes - r.n_downvotes, reverse=True)
        keywords = [{'url': '#', 'text': keyword} for keyword in paper.keywords.all()]
        return super().get_context_data(paper=paper, reviews=reviews, keywords=keywords, **kwargs)


orderings = {
    "new": Paper.latest,
    "trending": partial(Paper.trending, 100),
    "controversial": partial(Paper.controversial, 100)
}


class PapersView(TemplateView):
    template_name = "papers/list.html"
    order = ''

    def get_context_data(self, **kwargs):
        page = self.request.GET.get('page', '1')

        if not (page.isdigit() and int(page) >= 0):
            raise Http404

        page = int(page)
        paginator = Paginator(orderings[self.order](), 10)

        try:
            papers = paginator.page(page)
        except EmptyPage:
            page = paginator.num_pages
            papers = paginator.page(page)

        return super().get_context_data(order=self.order, papers=papers, **kwargs)

    def get_object(self, queryset=None):
        return queryset.get(name=self.name)

class ReviewView(BaseReviewView):
    template_name = "papers/comments.html"

    # Expands a tree so that each review in the tree gets its own form to edit the review
    def expand_tree(self, tree):
        return ReviewTree(
            review=self.add_review_fields(tree.review),
            level=tree.level,
            children=[self.expand_tree(child) for child in tree.children]
        )

    def get_context_data(self, **kwargs):
        if self.request.POST:
            return super().get_context_data(**kwargs)

        paper = self.objects.paper
        review = self.objects.review
        review.cache(select_related=("poster",))
        set_n_votes_cache(review._reviews.values())

        tree = self.expand_tree(review.get_tree())

        return super().get_context_data(tree=tree, paper=paper, **kwargs)

class SearchView(TemplateView):
    template_name = "papers/search.html"

    def get_context_data(self, **kwargs):
        query = self.request.GET.get('q', '')
        print(query)
        search_result = [x.object for x in SearchQuerySet().models(Paper).filter(content=query)]

        return dict(super().get_context_data(papers=search_result))

class AddPaperView(TemplateView):
  template_name = "papers/add.html"


@cache_page(60 * 10)
def doi_scraper(request, id):
    return HttpResponse(json.dumps({"error": "Invalid document identifier"}),
                        content_type="application/json")


def arxiv_scraper(request, doc_id):
    try:
        scraper_info = scrapers.Controller(scrapers.ArXivScraper).run(doc_id)
        scraper_info.update({'publish_date': scraper_info['publish_date'].strftime("%A, %d. %B %Y %I:%M%p")})
        return HttpResponse(json.dumps(scraper_info), content_type="application/json")
    except scrapers.ScraperError:
        return HttpResponse(json.dumps({"error": "Invalid document identifier"}),
                            content_type="application/json")
