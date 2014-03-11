from django.utils.functional import partition
from django.views.generic import TemplateView
from openreview.apps.main.models import Paper, Vote
from django.shortcuts import render

class PaperWithReviewsView(TemplateView):
    template_name = "papers/paper-with-reviews.html"

    def get(self, request, paper_id):
        upvotes, downvotes = set(), set()

        if not request.user.is_anonymous():
            votes = request.user.votes.filter(review__paper__id=paper_id, review__parent__isnull=True)
            votes = votes.only("id", "review__id", "vote")
            upvotes, downvotes = partition(lambda v: v.vote < 0, votes)

        return render(request, "papers/paper-with-reviews.html", {
            "paper": Paper.objects.get(pk=paper_id),
            "upvotes": {vote.review_id for vote in upvotes},
            "downvotes": {vote.review_id for vote in downvotes}
        })
