from django import forms
from django.forms import ModelForm
from openreview.apps.main.models import Vote


class VoteForm(ModelForm):
    vote = forms.IntegerField(min_value=-1, max_value=1)

    class Meta:
        model = Vote
        fields = ("vote",)