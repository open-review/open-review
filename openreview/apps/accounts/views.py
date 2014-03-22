from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.db import transaction
from django.views.generic import TemplateView, RedirectView

from openreview.apps.accounts.forms import RegisterForm, SettingsForm


class LoginView(TemplateView):
    template_name = "accounts/login.html"

    def __init__(self, *args, **kwargs):
        self.register_form = None
        self.login_form = None
        super().__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        register_data = self.request.POST if "new" in self.request.POST else None
        login_data = self.request.POST if "existing" in self.request.POST else None
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

    def dispatch(self, request, *args, **kwargs):
        settings_data = self.request.POST
        self.settings_form = SettingsForm(data=settings_data, user=request.user, auto_id='id_settings_%s')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return dict(super().get_context_data(**kwargs), settings_form=self.settings_form)

    def post(self, request):
        return self.update()

    def update(self):
        with transaction.atomic():
            if self.settings_form.is_valid():
                self.settings_form.save()
                return self.redirect()
        return self.get(self.request)

    def redirect(self):
       return redirect(self.request.GET.get("next", reverse("dashboard")), permanent=False)
