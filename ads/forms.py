from django import forms

from .models import Ad


class AdForm(forms.ModelForm):
    """Форма создания/редактирования объявления."""

    class Meta:
        model = Ad
        fields = (
            "category",
            "title",
            "description",
            "size",
            "brand",
            "price_per_day",
            "deposit",
            "city",
            "address",
            "contact_phone",
            "contact_email",
            "image",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "address": forms.TextInput(attrs={"placeholder": "Улица, дом"}),
        }
        help_texts = {
            "price_per_day": "Укажите стоимость аренды за одни сутки.",
            "deposit": "Залог возвращается после сдачи вещи.",
        }

    def clean_price_per_day(self):
        price = self.cleaned_data["price_per_day"]
        if price <= 0:
            raise forms.ValidationError("Стоимость аренды должна быть больше нуля.")
        return price

    def clean_contact_phone(self):
        phone = self.cleaned_data["contact_phone"].strip()
        if len(phone) < 5:
            raise forms.ValidationError("Слишком короткий номер телефона.")
        return phone


class AdSearchForm(forms.Form):
    """Форма поиска объявлений (не привязана к модели)."""

    q = forms.CharField(
        label="Ключевые слова",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Платье, костюм, смокинг...",
            }
        ),
    )
    city = forms.CharField(
        label="Город",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Москва"}),
    )
    min_price = forms.DecimalField(
        label="Цена от",
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"placeholder": "0"}),
    )
    max_price = forms.DecimalField(
        label="Цена до",
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"placeholder": "10000"}),
    )

    def clean(self):
        cleaned = super().clean()
        mn = cleaned.get("min_price")
        mx = cleaned.get("max_price")
        if mn is not None and mx is not None and mn > mx:
            raise forms.ValidationError(
                "Минимальная цена не может быть больше максимальной."
            )
        return cleaned
