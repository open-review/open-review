import json
from functools import partial

from django.core.paginator import Paginator, EmptyPage
from django.http import Http404
from django.shortcuts import HttpResponse, redirect
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_page
from haystack.query import SearchQuerySet
from django.views.generic import TemplateView

from openreview.apps.main.models import set_n_votes_cache, Review, Vote, Paper
from openreview.apps.tools.views import ModelViewMixin
from openreview.apps.papers import scrapers
from openreview.apps.papers.forms import PaperForm, ArXivForm


class BaseReviewView(ModelViewMixin, TemplateView):
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
            # We cannot pass a plain QuerySet to the template, as it would generate
            # way too much calls to the DBMS. Instead, we use .cache() and pass a
            # list of Review objects.
            review = paper.get_reviews()[0]
        except IndexError:
            reviews = []
        else:
            review.cache(select_related=["poster"])
            reviews = [r for r in review._reviews.values() if r.parent_id is None]

        related_by_author = set(Paper.objects.filter(authors__in=paper.authors.all()).exclude(id=paper.id)[:4])
        related_by_subject = set(Paper.objects.filter(keywords__in=paper.keywords.all()).exclude(id=paper.id)[:4])

        if len(related_by_subject) < 4:
            related_by_subject |= set(Paper.objects.filter(categories__in=paper.categories.all()).exclude(id=paper.id)[:4-len(related_by_subject)])

        # Set cache and sort reviews by up-/downvotes
        set_n_votes_cache(reviews)
        reviews.sort(key=lambda r: r.n_upvotes - r.n_downvotes, reverse=True)
        keywords = [{'url': '#', 'text': keyword} for keyword in paper.keywords.all()]
        return super().get_context_data(
            paper=paper, reviews=reviews, keywords=keywords, related_a=related_by_author,
            related_s=related_by_subject, **kwargs)


orderings = {
    "new": Paper.latest,
    "trending": partial(Paper.trending, 100),
    "controversial": partial(Paper.controversial, 100)
}


class PapersView(TemplateView):
    template_name = "papers/all.html"
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
    template_name = "papers/comment_thread.html"

    def get_context_data(self, **kwargs):
        paper = self.objects.paper
        review = self.objects.review
        review.cache(select_related=("poster",))
        set_n_votes_cache(review._reviews.values())

        return super().get_context_data(tree=review.get_tree(), paper=paper, review=review, **kwargs)


class SearchView(TemplateView):
    template_name = "papers/search_results.html"

    def get_context_data(self, **kwargs):
        query = self.request.GET.get('q') or ''
        search_results = ()

        if query:
            search_results = (x.object for x in SearchQuerySet().models(Paper).autocomplete(content_auto=query))
            # SearchQuerySet can end with 'None'. This filter will remove value from list.
            search_results = tuple(filter(bool, search_results))

        return dict(super().get_context_data(papers=search_results, query=query))


class AddPaperView(TemplateView):
    template_name = "papers/add.html"

    def get_context_data(self, **kwargs):
        manual_form_data = self.request.POST if 'manual_form' in self.request.POST else None
        arxiv_form_data = self.request.POST if 'arxiv_form' in self.request.POST else None

        manual_form = PaperForm(data=manual_form_data)
        arxiv_form = ArXivForm(data=arxiv_form_data)

        return dict(super().get_context_data(manual_form=manual_form, arxiv_form=arxiv_form))

    def post(self, request):
        if 'manual_form' in self.request.POST:
            # Try to add paper to db
            manual_form = PaperForm(data=self.request.POST)
            if manual_form.is_valid():
                paper = manual_form.save(commit=True)
                return redirect(reverse("paper", args=[paper.id]))
        elif 'arxiv_form' in self.request.POST:
            arxiv_form = ArXivForm(data=self.request.POST)
            if arxiv_form.is_valid():
                paper = arxiv_form.save(commit=True)
                return redirect(reverse("paper", args=[paper.id]))
        else:
            raise ValueError("Either `manual_form` or `arxiv_form` should be in POST parameters.")

        return super().get(request)

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
