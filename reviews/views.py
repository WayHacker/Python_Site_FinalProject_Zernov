from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from ads.models import Ad

from .forms import ReviewForm
from .models import Review


class AddReviewView(LoginRequiredMixin, View):
    """Добавление отзыва на объявление (только POST)."""

    def post(self, request, ad_pk):
        ad = get_object_or_404(Ad, pk=ad_pk)

        # Нельзя оставлять отзыв на своё объявление
        if ad.owner == request.user:
            messages.error(request, "Нельзя оставить отзыв на своё объявление.")
            return redirect(ad)

        # Один отзыв на объявление от одного пользователя
        if Review.objects.filter(ad=ad, author=request.user).exists():
            messages.error(request, "Вы уже оставили отзыв на это объявление.")
            return redirect(ad)

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.ad = ad
            review.author = request.user
            review.save()
            messages.success(request, "Спасибо за отзыв!")
        else:
            messages.error(request, "Проверьте форму отзыва.")

        return redirect(ad)
