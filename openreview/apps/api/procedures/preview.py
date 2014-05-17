from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.forms import ModelChoiceField, CharField
from django.shortcuts import render
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.views import APIView
from openreview.apps.main.forms import ReviewForm
from openreview.apps.main.models import Paper

class PreviewForm(ReviewForm):
    paper = ModelChoiceField(queryset=Paper.objects.all())
    text = CharField(required=False)

    def clean_rating(self):
        # Rating may also be not yet given in preview
        if self.cleaned_data['rating'] == -1:
            return -1
        return super().clean_rating()

    def save(self, commit=True):
        review = super().save(commit=False)
        review.paper = self.cleaned_data["paper"]
        return review

class PreviewProcedure(APIView):
    """Renders review as it would anywhere else on the website. This procedure
    always returns text/html. You can use the visibility parameter to render
    anonymous, public or external reviews. Your options are `public`,
    `semi_anonymous`, `anonymous`, and `external`. You need also provide a
    `paper` parameter."""
    def get(self, request, format=None):
        return Response({"details": "POST only."})

    @method_decorator(login_required)
    def post(self, request, format=None):
        preview_form = PreviewForm(user=request.user, data=request.DATA)
        if not preview_form.is_valid():
            return Response({"details": preview_form._errors}, status=400)

        # We need to set internal cache to prevent queries to an object which
        # does not exist in the database.
        review = preview_form.save(commit=False)
        review.id = 0
        review._n_comments = 0
        review._n_downvotes = 0
        review._n_upvotes = 0
        review._reviews_children = {0: []}
        review.timestamp = datetime.now()

        if not review.text:
            review.text = "*No text entered*"

        return render(request, "papers/review.html", {"review": review, "is_preview": True})
