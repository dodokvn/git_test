from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.accounts.interfaces.urls")),
    path("", include("apps.transfer_currency.interfaces.urls")),
]
