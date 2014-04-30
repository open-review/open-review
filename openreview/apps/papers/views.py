from functools import partial
import json
import datetime
from urllib import parse

from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponseForbidden, HttpResponseBadRequest, Http404
from django.shortcuts import render, HttpResponse, redirect
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.utils.datastructures import MultiValueDict
from django.views.generic import TemplateView, FormView

from openreview.apps.main.models import set_n_votes_cache, Review, Vote, Paper, ReviewTree
from openreview.apps.main.forms import ReviewForm
from openreview.apps.papers.forms import VoteForm
from openreview.apps.papers import scrapers
from openreview.apps.tools.auth import login_required
from openreview.apps.tools.views import ModelViewMixin

class VoteView(ModelViewMixin, FormView):
    """
    Allows voting on reviews. You can use the GET parameter 'vote' to cast one. For
    downvoting, upvoting or removing a vote use -1, 1 and 0 as value.
    """
    form_class = VoteForm
    template_name = "form.html"

    def get_form_kwargs(self):
        instance, _ = Vote.objects.get_or_create(voter=self.request.user, review=self.objects.review)
        return dict(super().get_form_kwargs(), instance=instance)

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response

    @method_decorator(login_required(raise_exception=False))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class BaseReviewView(ModelViewMixin, TemplateView):
    def redirect(self, review):
        review.cache()

        # Determine root of comment thread
        root = review
        while root.parent is not None:
            root = root.parent

        url = reverse("review", args=[review.paper_id, root.id])
        return redirect("{url}#r{review.id}".format(**locals()), permanent=False)

    def post(self, request, *args, **kwargs):
        # Is the user saving a new review?
        if self.creating_review():
            review_form = self.get_review_form()
            if review_form.is_valid():
                review = review_form.save()

                return self.redirect(review)
            else:
                return self.get(kwargs)

        # Is the user editing an existing review?
        # Note that the review's fields are submitted as '{review_id}-{fieldname}' on the paper page,
        # where multiple reviews may be edited. This is because fields should have unique names -
        # especially the star rating field, which is referenced to by name. We can recognize the field
        # name by finding which key named 'add_review{review_id}' is present in the POST-data.
        for key, value in self.request.POST.items():
            if key.startswith('add_review'):
                review_id = key[len('add_review'):]  # extract id from 'add_review{review_id}'
                review = Review.objects.get(id=review_id)

                review_form = self.get_review_edit_form(review)
                if review_form is None:
                    msg = "You are not the owner of the review or comment you are trying to edit"
                    return HttpResponseForbidden(msg)

                if review_form.is_valid():
                    review = review_form.save()
                    return self.redirect(review)

        return self.get(kwargs)

    def add_review_fields(self, review):
        return {
            'review': review,
            'form': self.get_review_edit_form(review),
            'submit_name': self.editing_review_name(review)
        }

    def creating_review(self):
        return "add_review" in self.request.POST

    def get_review_form(self):
        data = self.request.POST if self.creating_review() else None
        return ReviewForm(data=data, user=self.request.user, paper=self.objects.paper)

    def editing_review_name(self, review):
        return "add_review{}".format(review.id)

    def editing_review(self, review):
        return (self.editing_review_name(review)) in self.request.POST

    def get_review_edit_form(self, review):
        if review.poster != self.request.user:
            return

        args = {
            'user': self.request.user,
            'paper': self.objects.paper,
            'prefix': review.id,
            'instance': review
        }

        if self.editing_review(review):
            args['data'] = self.request.POST

        return ReviewForm(**args)

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
            add_review_form=self.get_review_form(),
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
        reviews = [self.add_review_fields(review) for review in reviews]
        
        keywords = [ { 'url' : '#', 'text' : keyword } for keyword in paper.keywords.all() ]
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


class PreviewView(BaseReviewView):
    @method_decorator(login_required(raise_exception=True))
    def post(self, request, paper_id, **kwargs):
        review = Review()
        review.poster = request.user
        review.paper = self.objects.paper
        review.timestamp = datetime.datetime.now()

        # Note that the review's text field can be either submitted as '{review_id}-text' (on the
        # paper page, where multiple reviews may be edited) or as 'text' (on the 'add review' page,
        # where only one review may be added). This is because fields should have unique names -
        # especially the star rating field, which is referenced to by name. This is easily solved
        # by taking any field that ends with 'text' as the review text.
        text = ""
        for key, value in request.POST.items():
            if key.endswith("text"):
                text = value

        review.text = text

        return render(request, "papers/review.html", {
            'paper': Paper.objects.get(id=paper_id),
            'review': review,
            'preview': True
        })


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

    @method_decorator(login_required(raise_exception=True))
    def patch(self, request, *args, **kwargs):
        review = self.objects.review

        if review.poster_id != self.request.user.id:
            return HttpResponseForbidden("You must be owner of this post in order to edit it.")

        # PATCH data is not standardised, but most javascript toolkits encode mappings as
        # normal urlencoded (POST-like) data, which we will try to interpret here.
        data = request.META['wsgi.input'].read()
        try:
            params = parse.parse_qs(data.decode("utf-8"))
        except UnicodeDecodeError:
            return HttpResponseBadRequest("Corrupt data. Encode is as UTF-8.")

        params = MultiValueDict(params)

        if "text" not in params:
            return HttpResponseBadRequest("You should provide 'text' in request data.")

        review.text = params["text"]
        review.save()
        return self.redirect(review)

    @method_decorator(login_required(raise_exception=True))
    def post(self, request, paper_id, review_id, **kwargs):
        commit = "submit" in request.POST

        if "text" not in request.POST:
            return HttpResponseBadRequest("You should provide 'text' in request data.")

        if "edit" in self.request.POST:
            review = Review.objects.get(id=self.request.POST["edit"])
            if review.poster != request.user:
                msg = "You are not the owner of the review or comment you are trying to edit"
                return HttpResponseForbidden(msg)
        else:
            review = Review()

        review.text = request.POST["text"]

        try:
            review.rating = int(self.request.POST.get("rating") or -1)
        except (ValueError, KeyError):
            return HttpResponseBadRequest("'rating' parameter should be specified and an integer.")

        if not review.has_valid_rating():
            return HttpResponseBadRequest("Specify a valid rating.")

        review.poster = request.user
        review.paper = self.objects.paper
        review.timestamp = datetime.datetime.now()

        if review_id != "-1":
            review.parent_id = self.objects.review.id
        else:
            review.parent = self.objects.review

        # Set cache, so we can use default template to render preview
        review._n_upvotes = 0
        review._n_downvotes = 0
        review._n_comments = 0

        if commit:
            try:
                review.save()
            except ValueError:
                msg = "Could not save review/comment due to incorrect values. Did you enter paper/review correctly?"
                return HttpResponseBadRequest(msg)

            return self.redirect(review)

        review.id = -1
        return render(request, "papers/review.html", {
            "paper": self.objects.paper,
            "review": review,
            "add_review_form": self.get_review_form(),
            "preview": True
        })

    @method_decorator(login_required(raise_exception=True))
    def delete(self, request, **kwargs):
        if request.user.id != self.objects.review.poster_id:
            return HttpResponseForbidden("You must be owner of this review/comment in order to delete it.")
        self.objects.review.delete()
        return HttpResponse("OK", status=200)


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
