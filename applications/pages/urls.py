from django.urls import path

from applications.pages.views import HomeView


app_name = "pages"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
]
