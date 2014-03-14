from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponse, HttpResponseNotFound

from django.utils.functional import partition
from django.views.generic import TemplateView,View
from django.shortcuts import render, HttpResponse
from django.views.decorators.cache import cache_page
import json

from .scrapers import ArXivScraper
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

        with transaction.atomic():
            Vote.objects.filter(review__id=review_id, voter=request.user).delete()
            if vote:
                Vote.objects.create(review_id=review_id, voter=request.user, vote=vote)

        return HttpResponse("OK", status=201)

class PaperWithReviewsView(TemplateView):
    template_name = "papers/paper-with-reviews.html"

    def get(self, request, paper_id):
        upvotes, downvotes = set(), set()

        if not request.user.is_anonymous():
            votes = request.user.votes.filter(review__paper__id=paper_id, review__parent__isnull=True)
            upvotes, downvotes = partition(lambda v: v.vote < 0, votes)

        paper = Paper.objects.prefetch_related("authors", "keywords").get(pk=paper_id)
        reviews = list(paper.get_reviews().select_related("poster"))
        set_n_votes_cache(reviews)
        reviews.sort(key=lambda r: r.n_upvotes - r.n_downvotes, reverse=True)

        return render(request, "papers/paper-with-reviews.html", {
            "paper": paper,
            "reviews": reviews,
            "upvotes": {vote.review_id for vote in upvotes},
            "downvotes": {vote.review_id for vote in downvotes}
        })


@cache_page(60*10)
def doi_scraper(request, id):
    return HttpResponse(json.JSONEncoder().encode({"error": "Invalid document identifier"}),
                        content_type="application/json")


def arxiv_scraper(request, id):
    try:
        tempres = ArXivScraper().parse(id)
        return HttpResponse(json.JSONEncoder().encode(tempres.get_results()), content_type="application/json")
    except Exception:
        return HttpResponse(json.JSONEncoder().encode({"error": "Invalid document identifier"}),
                            content_type="application/json")





