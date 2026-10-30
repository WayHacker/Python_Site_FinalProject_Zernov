import pytest
from django.urls import reverse

from users.models import User
from ads.models import Ad, Category
from .models import Review


@pytest.fixture
def owner(db):
    return User.objects.create_user(username="owner", password="pass12345")


@pytest.fixture
def guest(db):
    return User.objects.create_user(username="guest", password="pass12345")


@pytest.fixture
def ad(owner):
    cat, _ = Category.objects.get_or_create(
        slug="dresses",
        defaults={"name": "Платья"},
    )
    return Ad.objects.create(
        owner=owner,
        category=cat,
        title="Платье",
        description="x",
        size="M",
        price_per_day=100,
        city="M",
        contact_phone="+7",
        status=Ad.Status.APPROVED,
    )


@pytest.mark.django_db
class TestReviewCreation:
    def test_anonymous_cannot_review(self, client, ad):
        url = reverse("reviews:add", kwargs={"ad_pk": ad.pk})
        resp = client.post(url, {"rating": 5, "text": "ok"})
        # LoginRequiredMixin редиректит на логин
        assert resp.status_code == 302
        assert reverse("users:login") in resp.url
        assert not Review.objects.exists()

    def test_owner_cannot_review_own_ad(self, client, owner, ad):
        client.force_login(owner)
        url = reverse("reviews:add", kwargs={"ad_pk": ad.pk})
        resp = client.post(url, {"rating": 5, "text": "ok"})
        assert resp.status_code == 302
        assert not Review.objects.exists()

    def test_guest_can_review_once(self, client, guest, ad):
        client.force_login(guest)
        url = reverse("reviews:add", kwargs={"ad_pk": ad.pk})

        resp = client.post(url, {"rating": 4, "text": "Хорошо"})
        assert resp.status_code == 302
        assert Review.objects.count() == 1

        # повторный — не должен создаться
        client.post(url, {"rating": 5, "text": "Ещё раз"})
        assert Review.objects.count() == 1

    def test_invalid_rating_rejected(self, client, guest, ad):
        client.force_login(guest)
        url = reverse("reviews:add", kwargs={"ad_pk": ad.pk})
        resp = client.post(url, {"rating": 99, "text": "ok"})
        assert resp.status_code == 302
        assert not Review.objects.exists()

    def test_review_visible_on_detail(self, client, guest, ad):
        Review.objects.create(ad=ad, author=guest, rating=5, text="Супер")
        resp = client.get(reverse("ads:detail", kwargs={"pk": ad.pk}))
        content = resp.content.decode()
        assert "Супер" in content
        assert "guest" in content
