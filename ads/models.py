from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Категория одежды"""

    name = models.CharField("Название", max_length=100, unique=True)
    slug = models.SlugField("Слаг", max_length=100, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Ad(models.Model):
    """Объявление об аредне одежды"""

    class Status(models.TextChoices):
        PENDING = "pending", "На модерации"
        APPROVED = "approved", "Опубликовано"
        REJECTED = "rejected", "Отклонено"
        ARCHIVED = "archived", "В архиве"

    class Size(models.TextChoices):
        XS = "XS", "XS"
        S = "S", "S"
        M = "M", "M"
        L = "L", "L"
        XL = "XL", "XL"
        XXL = "XXL", "XXL"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ads",
        verbose_name="Владелец",
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="ads", verbose_name="Категория"
    )
    title = models.CharField("Заголовок", max_length=200)
    description = models.TextField("Описание")
    size = models.CharField("Размер", max_length=3, choices=Size.choices)
    brand = models.CharField("Бренд", max_length=100, blank=True)
    price_per_day = models.DecimalField(
        "Стоимость аренды в сутки",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    deposit = models.DecimalField(
        "Залог",
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    city = models.CharField("Город", max_length=100)
    address = models.CharField("Адрес", max_length=255, blank=True)
    contact_phone = models.CharField("Контактный телефон", max_length=20)
    contact_email = models.EmailField("Контактный email", blank=True)
    image = models.ImageField("Фото", upload_to="ads/", blank=True, null=True)

    status = models.CharField(
        "Статус",
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    moderation_comment = models.TextField(
        "Комментарий модератора",
        blank=True,
    )
    is_active = models.BooleanField("Активно", default=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "is_active"]),
            models.Index(fields=["city"]),
            models.Index(fields=["price_per_day"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def get_absolute_url(self):
        return reverse("ads:detail", kwargs={"pk": self.pk})

    @property
    def is_visible(self):
        """Видно ли объявление на сайте."""
        return self.status == self.Status.APPROVED and self.is_active
