from django import forms
from django.forms import ModelForm
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.views import APIView
from openreview.apps.main.models import Vote
from openreview.apps.tools.auth import login_required


class VoteProcedure(APIView):
    """
    A vote is *kinda* special as it does not cleanly map to a Vote object, as we
    generally don't care if a vote on the same review already exists: we just want
    to overwrite it.

    This procedure takes arguments `review` and `vote`.
    """
    def get(self, request, format=None):
        return Response({"details": "POST only."})

    @method_decorator(login_required)
    def post(self, request, format=None):
        vote_form = VoteForm(data=request.DATA)
        if not vote_form.is_valid():
            return Response({"details": vote_form._errors}, status=400)

        review = vote_form.cleaned_data["review"]
        vote, _ = Vote.objects.get_or_create(voter=request.user, review=review)
        vote.vote = vote_form.cleaned_data["vote"]
        vote.save()

        return Response({"details": "OK"}, status=201)


class VoteForm(ModelForm):
    vote = forms.IntegerField(min_value=-1, max_value=1)

    class Meta:
        model = Vote
        fields = ("vote", "review")
