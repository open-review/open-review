from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms import fields
from django.utils.translation import ugettext_lazy as _

class ReviewForm(forms.Form):
    """
    This is a monkey-patched version of django.contrib.auth.forms.UserCreationForm, which doesn't use
    get_user_model (as it should) but forces the internal auth User model.
    """
    error_messages = {

    }

    author_type = forms.ChoiceField(label=_("Author"),
                                widget=forms.RadioSelect(),
                                choices = [
                                    ("self", "Myself"),
                                    ("other", "Someone else"),
                                    ("anonimous", "Anonimous")
                                ],
                                help_text=_("Who is the author of this review? You can also choose not to publish the identity of the author."))
    author_name = forms.CharField(label=_("Name of author"),
                                help_text=_("What is the name of the author?"))
    
    content = forms.CharField(label=_("Contents"),
                                widget=forms.Textarea,
                                help_text=_("Enter the text of the review."))

    