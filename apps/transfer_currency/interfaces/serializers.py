# serializers.py
from rest_framework import serializers

from apps.transfer_currency.infrastructure.models import (
    Notification,
    Transaction,
    Wallet,
)
from apps.accounts.infrastructure.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone_number"]


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["id", "balance", "currency"]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "sender_wallet",
            "receiver_wallet",
            "amount",
            "created_at",
            "status",
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
