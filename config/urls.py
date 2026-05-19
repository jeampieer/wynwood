from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("", include("applications.pages.urls")),
    path("", include("applications.bookings.urls")),
    path("accounts/", include("applications.accounts.urls")),
    path("properties/", include("applications.properties.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
