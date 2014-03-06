from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms import fields
from django.utils.translation import ugettext_lazy as _

from openreview.apps.main.models.review import Review
from openreview.apps.main.models.author import Author

class ReviewForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(ReviewForm,self).__init__(*args, **kwargs)
        self.user = user


    error_messages = {

    }

    text = forms.CharField(label=_("Contents"),
                                widget=forms.Textarea,
                                help_text=_("Enter the text of the review."))

    def save(self, commit=True, **kwargs):
        user = super(ReviewForm,self).save(commit=False, **kwargs)
        user.poster = self.user
        if commit:
            user.save()
        return user


    class Meta:
        model = Review
        fields = ['paper','text'] 
