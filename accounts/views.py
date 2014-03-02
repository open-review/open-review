from django.contrib.auth import login, authenticate, logout

from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.db import transaction
from django.views.generic import TemplateView, RedirectView

from accounts.forms import RegisterForm


class LoginView(TemplateView):
    template_name = "accounts/login.html"

    def __init__(self, *args, **kwargs):
        self.register_form = None
        self.login_form = None
        super().__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.register_form = RegisterForm(data=self.request.POST if "new" in self.request.POST else None)
        self.login_form = AuthenticationForm(request=self.request, data=self.request.POST if "existing" in self.request.POST else None)
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

    @staticmethod
    def redirect():
        return redirect(reverse("frontpage"), permanent=False)

class LogoutView(RedirectView):
    permanent = False
    pattern_name = "frontpage"

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)
