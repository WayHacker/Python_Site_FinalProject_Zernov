from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("add/<int:ad_pk>/", views.AddReviewView.as_view(), name="add"),
]
