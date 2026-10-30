import pytest
from django.urls import reverse

from users.models import User
from .models import Ad, Category


@pytest.fixture
def category(db):
    cat, _ = Category.objects.get_or_create(
        slug="dresses",
        defaults={"name": "Платья"},
    )
    return cat


@pytest.fixture
def owner(db):
    return User.objects.create_user(username="owner", password="pass12345")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="other", password="pass12345")


@pytest.fixture
def approved_ad(owner, category):
    return Ad.objects.create(
        owner=owner,
        category=category,
        title="Красное платье",
        description="Красивое длинное",
        size="M",
        price_per_day=1000,
        city="Москва",
        contact_phone="+79990000000",
        status=Ad.Status.APPROVED,
    )


# ---------------------------------------------------------------------------
# Публикация / модерация
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAdCreation:
    def test_create_requires_login(self, client):
        resp = client.get(reverse("ads:create"))
        assert resp.status_code == 302
        assert reverse("users:login") in resp.url

    def test_create_sets_pending_status(self, client, owner, category):
        client.force_login(owner)
        resp = client.post(
            reverse("ads:create"),
            {
                "category": category.pk,
                "title": "Новое платье",
                "description": "Описание",
                "size": "L",
                "brand": "",
                "price_per_day": "700.00",
                "deposit": "0.00",
                "city": "Казань",
                "address": "",
                "contact_phone": "+79991234567",
                "contact_email": "",
            },
        )
        assert resp.status_code == 302
        ad = Ad.objects.get(title="Новое платье")
        assert ad.status == Ad.Status.PENDING
        assert ad.owner == owner

    def test_price_must_be_positive(self, client, owner, category):
        client.force_login(owner)
        resp = client.post(
            reverse("ads:create"),
            {
                "category": category.pk,
                "title": "Плохое",
                "description": "x",
                "size": "S",
                "price_per_day": "0",
                "deposit": "0",
                "city": "М",
                "contact_phone": "+7",
            },
        )
        assert resp.status_code == 200  # остались на форме
        assert not Ad.objects.filter(title="Плохое").exists()


# ---------------------------------------------------------------------------
# Список и поиск
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAdListAndSearch:
    def test_only_approved_visible(self, client, owner, category, approved_ad):
        Ad.objects.create(
            owner=owner,
            category=category,
            title="Скрытое",
            description="x",
            size="S",
            price_per_day=500,
            city="СПб",
            contact_phone="+7",
            status=Ad.Status.PENDING,
        )
        resp = client.get(reverse("ads:list"))
        content = resp.content.decode()
        assert "Красное платье" in content
        assert "Скрытое" not in content

    def test_search_by_keyword(self, client, approved_ad):
        resp = client.get(reverse("ads:list"), {"q": "Красное"})
        assert "Красное платье" in resp.content.decode()

        resp = client.get(reverse("ads:list"), {"q": "синее"})
        assert "Красное платье" not in resp.content.decode()

    def test_search_by_city(self, client, approved_ad):
        resp = client.get(reverse("ads:list"), {"city": "Москва"})
        assert "Красное платье" in resp.content.decode()

        resp = client.get(reverse("ads:list"), {"city": "Питер"})
        assert "Красное платье" not in resp.content.decode()

    def test_search_by_price_range(self, client, approved_ad):
        resp = client.get(
            reverse("ads:list"),
            {
                "min_price": "500",
                "max_price": "2000",
            },
        )
        assert "Красное платье" in resp.content.decode()

        resp = client.get(reverse("ads:list"), {"min_price": "5000"})
        assert "Красное платье" not in resp.content.decode()

    def test_invalid_price_range(self, client, approved_ad):
        resp = client.get(
            reverse("ads:list"),
            {
                "min_price": "5000",
                "max_price": "100",
            },
        )
        # форма невалидна → фильтр не применяется → видим все одобренные
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Редактирование / удаление — только владелец
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAdOwnership:
    def test_edit_forbidden_for_non_owner(
        self,
        client,
        other_user,
        approved_ad,
    ):
        client.force_login(other_user)
        resp = client.get(reverse("ads:edit", kwargs={"pk": approved_ad.pk}))
        assert resp.status_code == 403

    def test_delete_forbidden_for_non_owner(
        self,
        client,
        other_user,
        approved_ad,
    ):
        client.force_login(other_user)
        resp = client.get(reverse("ads:delete", kwargs={"pk": approved_ad.pk}))
        assert resp.status_code == 403

    def test_owner_can_edit_and_resets_to_pending(
        self,
        client,
        owner,
        approved_ad,
    ):
        client.force_login(owner)
        resp = client.post(
            reverse("ads:edit", kwargs={"pk": approved_ad.pk}),
            {
                "category": approved_ad.category.pk,
                "title": "Красное платье (обновлено)",
                "description": "Обновлено",
                "size": "M",
                "price_per_day": "1500",
                "deposit": "0",
                "city": "Москва",
                "contact_phone": "+79990000000",
            },
        )
        assert resp.status_code == 302
        approved_ad.refresh_from_db()
        assert approved_ad.title == "Красное платье (обновлено)"
        assert approved_ad.status == Ad.Status.PENDING

    def test_owner_can_delete(self, client, owner, approved_ad):
        client.force_login(owner)
        resp = client.post(
            reverse("ads:delete", kwargs={"pk": approved_ad.pk}),
        )
        assert resp.status_code == 302
        assert not Ad.objects.filter(pk=approved_ad.pk).exists()


# ---------------------------------------------------------------------------
# Контакты — только авторизованным
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestContactsVisibility:
    def test_anonymous_cannot_see_phone(self, client, approved_ad):
        resp = client.get(
            reverse("ads:detail", kwargs={"pk": approved_ad.pk}),
        )
        assert approved_ad.contact_phone not in resp.content.decode()

    def test_authenticated_sees_phone(
        self,
        client,
        other_user,
        approved_ad,
    ):
        client.force_login(other_user)
        resp = client.get(
            reverse("ads:detail", kwargs={"pk": approved_ad.pk}),
        )
        assert approved_ad.contact_phone in resp.content.decode()
