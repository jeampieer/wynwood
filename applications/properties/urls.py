from django.urls import path

from applications.properties.api_views import PropertyDetailApiView, PropertyListApiView
from applications.properties.views import PropertyDetailView, PropertySearchView


app_name = "properties"

urlpatterns = [
    path("search/", PropertySearchView.as_view(), name="search"),
    path("<slug:slug>/", PropertyDetailView.as_view(), name="detail"),
    path("api/properties/", PropertyListApiView.as_view(), name="api-list"),
    path("api/properties/<slug:slug>/", PropertyDetailApiView.as_view(), name="api-detail"),
]
