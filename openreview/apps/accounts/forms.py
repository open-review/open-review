from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms import fields
from django.utils.translation import ugettext_lazy as _


def is_email(string):
    try:
        validate_email(string)
    except ValidationError:
        return False
    return True


class UserCreationForm(forms.ModelForm):
    """
    This is a monkey-patched version of django.contrib.auth.forms.UserCreationForm, which doesn't use
    get_user_model (as it should) but forces the internal auth User model.
    """
    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    username = forms.RegexField(label=_("Username"), max_length=30,
                                regex=r'^[\w.@+-]+$',
                                help_text=_("Required. 30 characters or fewer. Letters, digits and "
                                            "@/./+/-/_ only."),
                                error_messages={
                                    'invalid': _("This value may contain only letters, numbers and "
                                                 "@/./+/-/_ characters.")})
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = get_user_model()
        fields = ("username",)

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            get_user_model()._default_manager.get(username=username)
        except get_user_model().DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class RegisterForm(UserCreationForm):
    """

    """
    email = fields.EmailField(required=False, label=_("E-mail address (optional)"),
                              help_text=_("E-mail addresses are used for password recovery only."))

    def clean_username(self):
        user = super().clean_username()
        if is_email(user):
            raise ValidationError(_("Valid e-mail addresses can't be used as username."), code='invalid')
        return user

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
        return user

    class Meta:
        model = get_user_model()
        fields = ("username", "password1", "password2", "email")


class SettingsForm(RegisterForm):
    """

    """
    title = forms.CharField(help_text=_('e.g. "MSc" in "Pietje Puk (Msc, University of Twente)"'))
    university = forms.CharField(help_text=_('e.g. "University of Twente" in "Pietje Puk (Msc, University of Twente)"'))

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["password1"].required = False
        self.fields["password2"].required = False
        self.fields.pop("username")

    def save(self, commit=True):
        password = self.cleaned_data["password1"]
        email = self.cleaned_data["email"]
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        title = self.cleaned_data["title"]
        university = self.cleaned_data["university"]
        if password:
            self.user.set_password(password)
        if email:
            self.user.email = email
        if title:
            self.user.title = title
        if first_name:
            self.user.first_name = first_name
        if last_name:
            self.user.last_name = last_name
        if university:
            self.user.university = university
        if commit:
            self.user.save()
        return self.user

    class Meta:
        model = get_user_model()
        fields = ("password1", "password2", "email", "first_name", "last_name", "title", "university")
        exclude = ["username"]


class AccountDeleteForm(forms.ModelForm):
    error_messages = {
        'wrong_password': _("The entered password is wrong."),
    }

    DELETE_CHOICES = (('keep_reviews', 'Delete my account, but preserve reviews (making them anonymous).'),
                      ('delete_all', 'Delete my account, including reviews.'))

    password = forms.CharField(label=_("password"), widget=forms.PasswordInput)
    option = forms.ChoiceField(choices=DELETE_CHOICES, widget=forms.RadioSelect(), initial="keep_reviews")

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError(
                self.error_messages['wrong_password'],
                code='wrong_password',
            )
        return password

    def save(self, commit=True):
        choice = self.cleaned_data['option']
        self.user.delete(delete_reviews=choice == "delete_all")

    class Meta:
        model = get_user_model()
        fields = ("password", "option")
