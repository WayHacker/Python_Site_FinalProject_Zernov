from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    """Форма отзыва на объявление."""

    class Meta:
        model = Review
        fields = ("rating", "text")
        widgets = {
            "rating": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 5,
                    "step": 1,
                }
            ),
            "text": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Расскажите о своём опыте аренды...",
                }
            ),
        }
        labels = {
            "rating": "Оценка (1–5)",
            "text": "Ваш отзыв",
        }
