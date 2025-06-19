# serializers.py
from rest_framework import serializers

from transfer_currency.infrastructure.models import (
    Notification,
    Transaction,
    User,
    Wallet,
)


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
            "timestamp",
            "status",
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
