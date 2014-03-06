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

    """author_type = forms.ChoiceField(label=_("Author"),
                                widget=forms.RadioSelect(),
                                choices = [
                                    ("self", "Myself"),
                                    ("other", "Someone else"),
                                    (None, "Anonimous")
                                ],
                                help_text=_("Who is the author of this review? You can also choose not to publish the identity of the author."))
    poster = forms.CharField(label=_("Name of author"),
                               help_text=_("What is the name of the author?"),
                               required= False)
    """
    text = forms.CharField(label=_("Contents"),
                                widget=forms.Textarea,
                                help_text=_("Enter the text of the review."))

    """def clean_poster(self):
        if Author.objects.filter(name=self.data['poster']):
            return Author.objects.get(name=self.data['poster'])
        else:
            return Author.objects.create(name=self.data['poster'])
    """
    def clean_text(self):
        return self.data['text'].replace("\n","<br/>\n")

    def save(self, commit=True, **kwargs):
        user = super(ReviewForm,self).save(commit=False, **kwargs)
        user.poster = self.user
        if commit:
            user.save()
        return user


    class Meta:
        model = Review
        fields = ['paper','text'] #author_type','poster','paper','text']
