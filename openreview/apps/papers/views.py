import json
import datetime

from urllib import parse
from django.core.paginator import Paginator, EmptyPage

from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotFound, Http404
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotFound, Http404

from django.shortcuts import render, HttpResponse, redirect
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.utils.datastructures import MultiValueDict
from django.views.generic import TemplateView, View

from .scrapers import ArXivScraper
from openreview.apps.main.models import set_n_votes_cache, Review, Vote, Paper, ReviewTree
from openreview.apps.main.forms import ReviewForm
from openreview.apps.tools.auth import login_required
from openreview.apps.tools.views import ModelViewMixin

PAGE_COUNT = 25
PAGINATION_COUNT = 6

class VoteView(View):
    def get(self, request, paper_id, review_id):
        if request.user.is_anonymous():
            return HttpResponseForbidden("You must be logged in to vote")

        if not Review.objects.filter(id=review_id).exists():
            return HttpResponseNotFound("Review with id {review_id} does not exist.".format(**locals()))

        try:
            vote = int(self.request.GET["vote"])
        except (ValueError, KeyError):
            return HttpResponseBadRequest("No vote value, or non-int given.")

        if not (-1 <= vote <= 1):
            return HttpResponseBadRequest("You can only vote -1, 0 or 1.")

        review = Review.objects.defer("text").get(id=review_id)
        with transaction.atomic():
            review._invalidate_template_caches()
            Vote.objects.filter(review__id=review_id, voter=request.user).delete()
            if vote:
                Vote.objects.create(review_id=review_id, voter=request.user, vote=vote)

        return HttpResponse("OK", status=201)

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
        # Note that the review's fields are submitted as '{review_id}-{fieldname}' on the paper page, where multiple reviews may be edited
        # This is because fields should have unique names - especially the star rating field, which is referenced to by name.
        # We can recognize the field name by finding which key named 'add_review{review_id}' is present in the POST-data.
        for key, value in self.request.POST.items():
            if key.startswith('add_review'):
                review_id = key[len('add_review'):] # extract id from 'add_review{review_id}'
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

        return super().get_context_data(paper=paper, reviews=reviews, **kwargs)


class PapersView(TemplateView):
    template_name = "papers/overview.html"
    order = ''

    def get_context_data(self, **kwargs):     
        try:      
            page = int(self.request.GET.get('p', '1'))
        except ValueError:
            raise Http404

        if not page >= 0:
            raise Http404

        if self.order == 'new':
            source = Paper.latest()
            title = "New"
        elif self.order == 'trending':
            source = Paper.trending(100)
            title = "Trending"
        elif self.order == 'controversial':            
            source = Paper.controversial(100)
            title = "Controversial"      

        paginator = Paginator(source, PAGE_COUNT)
        try:
            papers = paginator.page(page)
        except EmptyPage:
            page = paginator.num_pages
            papers = paginator.page(page)

        pages_right = paginator.page_range[page:]
        pages_left = paginator.page_range[0:page-1]

        return dict(super().get_context_data(title=title, papers=papers, cur_page=page, pages_l=pages_left, pages_r=pages_right, pag_max=PAGINATION_COUNT, **kwargs))                           

    def get_object(self, queryset=None):
        return queryset.get(name=self.name)


class PreviewView(BaseReviewView):
    @method_decorator(login_required(raise_exception=True))
    def post(self, request, paper_id, **kwargs):
        review = Review()
        review.poster = request.user
        review.paper = self.objects.paper
        review.timestamp = datetime.datetime.now()

        # Note that the review's text field can be either submitted as '{review_id}-text' (on the paper page, where multiple reviews may be edited) or as 'text' (on the 'add review' page, where only one review may be added)
        # This is because fields should have unique names - especially the star rating field, which is referenced to by name.
        # This is easily solved by taking any field that ends with 'text' as the review text.
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
        
        tree=self.expand_tree(review.get_tree())

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
            if (review.poster != request.user):
                msg = "You are not the owner of the review or comment you are trying to edit"
                return HttpResponseForbidden(msg)
        else:
            review = Review()

        review.text = request.POST["text"]

        try:
            vote = int(self.request.POST["rating"])
        except (ValueError, KeyError):
            vote = 0

        if not (1 <= vote <= 7):
            vote = 0

        review.rating = vote
        review.poster = request.user
        review.paper = self.objects.paper
        review.timestamp = datetime.datetime.now()

        if review_id != "-1":
            review.parent_id = int(review_id)

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
        return render(request, "papers/review.html", dict(paper=self.objects.paper, review=review, add_review_form=self.get_review_form()))

    @method_decorator(login_required(raise_exception=True))
    def delete(self, request, **kwargs):
        if request.user.id != self.objects.review.poster_id:
            return HttpResponseForbidden("You must be owner of this review/comment in order to delete it.")
        self.objects.review.delete()
        return HttpResponse("OK", status=200)


@cache_page(60*10)
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

