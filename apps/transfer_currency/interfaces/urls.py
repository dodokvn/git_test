from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import (
    NotificationViewSet,
    TransactionViewSet,
    WalletCreateView,
    WalletViewSet,
)

router = DefaultRouter()
# router.register(r"users", UserViewSet)
router.register(r"wallets", WalletViewSet)
router.register(r"transactions", TransactionViewSet)
router.register(r"notifications", NotificationViewSet)

urlpatterns = [
    # pages HTML
    path("", views.HomeView.as_view(), name="home"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("transfer/", views.ImmediateTransferView.as_view(), name="create_transfer"),
    path("wallet/create/", WalletCreateView.as_view(), name="create_wallet"),
    path(
        "transfer/schedule/",
        views.ScheduleTransferView.as_view(),
        name="schedule_transfer",
    ),
    path(
        "transaction/<int:pk>/",
        views.TransactionDetailView.as_view(),
        name="transaction_detail",
    ),
    path("notifications/", views.NotificationListView.as_view(), name="notifications"),
    path(
        "scheduled-transfer/cancel/<int:pk>/",
        views.CancelScheduledTransferView.as_view(),
        name="cancel_scheduled_transfer",
    ),
    # API
    path("api/", include(router.urls)),
]
