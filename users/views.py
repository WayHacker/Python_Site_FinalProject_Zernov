from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserRegisterForm


class RegisterView(CreateView):
    """Регистрация нового пользователя."""

    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("ads:list")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("ads:list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)
