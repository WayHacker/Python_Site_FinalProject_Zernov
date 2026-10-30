import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
class TestRegistration:
    def test_register_creates_user_and_logs_in(self, client):
        resp = client.post(
            reverse("users:register"),
            {
                "username": "newbie",
                "email": "new@example.com",
                "phone": "+79991234567",
                "password1": "Str0ngPass!",
                "password2": "Str0ngPass!",
            },
        )
        assert resp.status_code == 302
        assert resp.url == reverse("ads:list")
        user = User.objects.get(username="newbie")
        assert user.phone == "+79991234567"
        # залогинен после регистрации
        assert client.session["_auth_user_id"] == str(user.pk)

    def test_register_duplicate_email_fails(self, client):
        User.objects.create_user(
            username="existing",
            email="dup@example.com",
            password="pass12345",
        )
        resp = client.post(
            reverse("users:register"),
            {
                "username": "newbie",
                "email": "dup@example.com",
                "phone": "+79990000000",
                "password1": "Str0ngPass!",
                "password2": "Str0ngPass!",
            },
        )
        assert resp.status_code == 200  # остались на странице
        assert "уже зарегистрирован" in resp.content.decode()
        assert not User.objects.filter(username="newbie").exists()

    def test_register_page_redirects_if_authenticated(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username="u",
            password="pass12345",
        )
        client.force_login(user)
        resp = client.get(reverse("users:register"))
        assert resp.status_code == 302
        assert resp.url == reverse("ads:list")


@pytest.mark.django_db
class TestAuth:
    def test_login_works(self, client, django_user_model):
        django_user_model.objects.create_user(
            username="alice",
            password="pass12345",
        )
        resp = client.post(
            reverse("users:login"),
            {
                "username": "alice",
                "password": "pass12345",
            },
        )
        assert resp.status_code == 302

    def test_logout_via_post(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username="alice",
            password="pass12345",
        )
        client.force_login(user)
        resp = client.post(reverse("users:logout"))
        assert resp.status_code == 302
        assert "_auth_user_id" not in client.session
