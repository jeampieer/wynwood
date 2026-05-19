from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core import views as core_views


urlpatterns = [
    path("", include("applications.pages.urls")),
    path("", include("applications.bookings.urls")),
    path("api/v1/", include("config.api_urls")),
    path("accounts/", include("applications.accounts.urls")),
    path("properties/", include("applications.properties.urls")),
    path("health/", core_views.health, name="health"),
    path("health/ping/", core_views.ping, name="health-ping"),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
