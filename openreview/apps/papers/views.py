from django.utils.functional import partition
from django.views.generic import TemplateView
from django.shortcuts import render

from openreview.apps.main.models import Paper, set_n_votes_cache


class PaperWithReviewsView(TemplateView):
    template_name = "papers/paper-with-reviews.html"

    def get(self, request, paper_id):
        upvotes, downvotes = set(), set()

        if not request.user.is_anonymous():
            votes = request.user.votes.filter(review__paper__id=paper_id, review__parent__isnull=True)
            votes = votes.only("id", "review__id", "vote")
            upvotes, downvotes = partition(lambda v: v.vote < 0, votes)

        paper = Paper.objects.prefetch_related("authors", "keywords").get(pk=paper_id)
        reviews = paper.get_reviews().select_related("poster")
        set_n_votes_cache(reviews)

        return render(request, "papers/paper-with-reviews.html", {
            "paper": paper,
            "reviews": reviews,
            "upvotes": {vote.review_id for vote in upvotes},
            "downvotes": {vote.review_id for vote in downvotes}
        })
