from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path("api/property/", include("property.urls")),
    path("api/booking/", include("booking.urls")),
    path("api/hostels/", include("hostels.urls")),
    path("api/hotels/", include("hotels.urls")),
    path("api/services/", include("services.urls")),
]
