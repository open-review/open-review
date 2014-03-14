import json

from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponse, HttpResponseNotFound
from django.views.generic import TemplateView, View

from openreview.apps.main.models import Paper, set_n_votes_cache, Review, Vote


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

class BaseReviewView(TemplateView):
    def get_context_data(self, **kwargs):
        if self.request.user.is_anonymous():
            return super().get_context_data(**kwargs)

        # Passing reviews and votes of user allows efficient caching of templates
        # as we gain the possibility to let javascript do the markup
        my_reviews = Review.objects.filter(paper__id=self.kwargs["paper_id"], poster=self.request.user)
        my_reviews = tuple(my_reviews.values_list("id", flat=True))

        my_votes = Vote.objects.filter(review__paper__id=self.kwargs["paper_id"], voter=self.request.user)
        my_votes = dict(my_votes.values_list("review__id", "vote"))

        return super().get_context_data(
            my_reviews=json.dumps(my_reviews),
            my_votes=json.dumps(my_votes),
            **kwargs
        )

class PaperWithReviewsView(BaseReviewView):
    template_name = "papers/paper.html"

    def get_context_data(self, **kwargs):
        paper = Paper.objects.prefetch_related("authors", "keywords").get(pk=self.kwargs["paper_id"])
        reviews = list(paper.get_reviews().select_related("poster"))
        set_n_votes_cache(reviews)
        reviews.sort(key=lambda r: r.n_upvotes - r.n_downvotes, reverse=True)
        return super().get_context_data(paper=paper, reviews=reviews, **kwargs)

class ReviewView(BaseReviewView):
    template_name = "papers/comments.html"

    def get_context_data(self, **kwargs):
        review = Review.objects.get(id=self.kwargs["review_id"])
        paper = Paper.objects.get(id=self.kwargs["paper_id"])
        review.cache(select_related=("poster",))
        set_n_votes_cache(review._reviews.values())
        tree = review.get_tree()
        return super().get_context_data(tree=tree, paper=paper, **kwargs)


