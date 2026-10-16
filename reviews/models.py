from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """Отзывы на объявление"""

    ad = models.ForeignKey(
        "ads.Ad",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Объявление",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор",
    )
    rating = models.PositiveSmallIntegerField(
        "Оценка", validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField("Текст отзыва")
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["ad", "author"], name="unique_review_per_user_per_ad"
            )
        ]

    def __str__(self):
        return f'{self.author} -> {self.ad} ({self.rating} star)'
