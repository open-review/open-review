from django import forms
from django.utils.translation import ugettext_lazy as _

from openreview.apps.main.models.review import Review

class ReviewForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.user = user

    text = forms.CharField(label=_("Contents"),
                           widget=forms.Textarea,
                           help_text=_("Enter the text of the review."))

    def save(self, commit=True, **kwargs):
        user = super(ReviewForm, self).save(commit=False, **kwargs)
        user.poster = self.user
        if commit:
            user.save()
        return user

    class Meta:
        model = Review
        fields = ['paper', 'text']
