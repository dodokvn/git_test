from django.contrib import admin
from .models import Notification, Transaction, Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "balance", "currency")
    search_fields = ("user__username", "currency")
    list_filter = ("currency",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sender_wallet",
        "receiver_wallet",
        "amount",
        "timestamp",
        "scheduled",
        "event",
        "status",
    )
    search_fields = (
        "sender_wallet__user__username",
        "receiver_wallet__user__username",
        "event",
    )
    list_filter = ("status", "timestamp")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "message", "timestamp", "is_read")
    search_fields = ("user__username", "message")
    list_filter = ("is_read", "timestamp")
