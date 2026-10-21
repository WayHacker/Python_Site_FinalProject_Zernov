from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import AdForm, AdSearchForm
from .models import Ad, Category


class AdListView(ListView):
    """Список опубликованных объявлений с поиском."""

    model = Ad
    template_name = "ads/ad_list.html"
    context_object_name = "ads"
    paginate_by = 12

    def get_queryset(self):
        qs = Ad.objects.filter(
            status=Ad.Status.APPROVED, is_active=True
        ).select_related("owner", "category")

        self.form = AdSearchForm(self.request.GET or None)
        if self.form.is_valid():
            data = self.form.cleaned_data

            q = data.get("q")
            if q:
                qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

            city = data.get("city")
            if city:
                qs = qs.filter(city__icontains=city)

            min_price = data.get("min_price")
            if min_price is not None:
                qs = qs.filter(price_per_day__gte=min_price)

            max_price = data.get("max_price")
            if max_price is not None:
                qs = qs.filter(price_per_day__lte=max_price)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form"] = self.form
        ctx["categories"] = Category.objects.all()
        return ctx


class AdDetailView(DetailView):
    """Детальная страница объявления."""

    model = Ad
    template_name = "ads/ad_detail.html"
    context_object_name = "ad"

    def get_queryset(self):
        return Ad.objects.select_related("owner", "category")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["reviews"] = self.object.reviews.select_related("author")

        if self.request.user.is_authenticated:
            from reviews.forms import ReviewForm
            from reviews.models import Review

            ctx["review_form"] = ReviewForm()
            ctx["can_review"] = (
                self.object.owner != self.request.user
                and not Review.objects.filter(
                    ad=self.object, author=self.request.user
                ).exists()
            )
        return ctx


class AdCreateView(LoginRequiredMixin, CreateView):
    """Создание объявления (статус — на модерации)."""

    model = Ad
    form_class = AdForm
    template_name = "ads/ad_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.status = Ad.Status.PENDING
        messages.success(
            self.request,
            "Объявление отправлено на модерацию. "
            "После проверки оно появится на сайте.",
        )
        return super().form_valid(form)


class AdUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование — только владелец."""

    model = Ad
    form_class = AdForm
    template_name = "ads/ad_form.html"

    def test_func(self):
        return self.get_object().owner == self.request.user

    def form_valid(self, form):
        form.instance.status = Ad.Status.PENDING
        messages.info(self.request, "Изменения отправлены на модерацию.")
        return super().form_valid(form)


class AdDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление — только владелец."""

    model = Ad
    template_name = "ads/ad_confirm_delete.html"
    success_url = reverse_lazy("ads:my_ads")

    def test_func(self):
        return self.get_object().owner == self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Объявление удалено.")
        return super().form_valid(form)


class MyAdsView(LoginRequiredMixin, ListView):
    """Мои объявления."""

    model = Ad
    template_name = "ads/my_ads.html"
    context_object_name = "ads"

    def get_queryset(self):
        return (
            Ad.objects.filter(owner=self.request.user)
            .select_related("category")
            .order_by("-created_at")
        )
