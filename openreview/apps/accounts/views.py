from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.db import transaction
from django.views.generic import TemplateView, RedirectView
from django.utils.decorators import method_decorator
from openreview.apps.main.models.review import set_n_votes_cache

from openreview.apps.accounts.forms import RegisterForm, SettingsForm, AccountDeleteForm


class AuthenticationView(TemplateView):
    template_name = "accounts/authentication.html"

    def __init__(self, *args, **kwargs):
        self.register_form = None
        self.login_form = None
        super().__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        register_data = self.request.POST if "new" in self.request.POST else None
        login_data = self.request.POST if "login" in self.request.POST else None
        self.register_form = RegisterForm(data=register_data, auto_id='id_register_%s')
        self.login_form = AuthenticationForm(request=self.request, data=login_data, auto_id='id_login_%s')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return dict(super().get_context_data(**kwargs), login_form=self.login_form, register_form=self.register_form)

    def post(self, request):
        return self.register() if "new" in request.POST else self.login()

    def register(self):
        with transaction.atomic():
            if self.register_form.is_valid():
                username = self.register_form.cleaned_data["username"]
                password = self.register_form.cleaned_data["password1"]
                self.register_form.save()
                login(self.request, authenticate(username=username, password=password))
                return self.redirect()
        return self.get(self.request)

    def login(self):
        if not self.login_form.is_valid():
            return self.get(self.request)
        login(self.request, self.login_form.get_user())
        return self.redirect()

    def redirect(self):
        # Redirect to GET parameter 'next', or dashboard
        return redirect(self.request.GET.get("next", reverse("dashboard")), permanent=False)


class LogoutView(RedirectView):
    permanent = False
    pattern_name = "dashboard"

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class SettingsView(TemplateView):
    template_name = "accounts/settings.html"

    def __init__(self, *args, **kwargs):
        self.settings_form = None
        super().__init__(*args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.settings_form = SettingsForm(data=request.POST or None, instance=request.user)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        if self.settings_form.is_valid():
            self.settings_form.save()
        return redirect(reverse("accounts-settings"))

    def get(self, request):
        reviews = request.user.reviews.all()
        set_n_votes_cache(reviews)
        return super().get(request, reviews=reviews, settings_form=self.settings_form)

class AccountDeleteView(TemplateView):
    template_name = "accounts/delete.html"

    def __init__(self, *args, **kwargs):
        self.delete_form = None
        super().__init__(*args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        delete_data = request.POST or None
        self.delete_form = AccountDeleteForm(request.user, data=delete_data)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return super().get(request, delete_form=self.delete_form)

    def post(self, request):
        self.delete_form.is_valid()
        return self.update()

    def update(self):
        if self.delete_form.is_valid():
            self.delete_form.save()
            return redirect(reverse("landing_page"))
        return redirect(reverse("accounts-delete"))
