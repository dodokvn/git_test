from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from transfer_currency.domain.entities import TransactionEntity
from django.conf import settings

User = get_user_model()


class TransactionStatusChoices(models.TextChoices):
    PENDING = "PENDING", "Pending"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
    SCHEDULED = "SCHEDULED", "Scheduled"


class CurrencyChoices(models.TextChoices):
    USD = "USD", "USD - US Dollar"
    EUR = "EUR", "EUR - Euro"
    BIF = "BIF", "BIF - Burundian Franc"
    KES = "KES", "KES - Kenyan Shilling"


CONVERSION_RATES = {
    "USD": {"USD": 1, "EUR": 0.9, "BIF": 2850, "KES": 120},
    "EUR": {"USD": 1.1, "EUR": 1, "BIF": 3150, "KES": 130},
    "BIF": {"USD": 0.00035, "EUR": 0.00031, "BIF": 1, "KES": 0.041},
    "KES": {"USD": 0.0083, "EUR": 0.0077, "BIF": 24.3, "KES": 1},
}


class TimeAbstractModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_deleted",
    )
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        self.deleted_at = timezone.now()
        if user and isinstance(user, User):
            self.deleted_by = user
        self.save()

    def hard_delete_if_soft_deleted(self):
        if self.deleted_at is not None:
            super().delete()


class Wallet(TimeAbstractModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    balance = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=10, choices=CurrencyChoices.choices)

    class Meta:
        app_label = "transfer_currency"

    @staticmethod
    def get_converted_amount(
        amount: Decimal, target_currency: str, source_currency: str
    ) -> Decimal:
        if source_currency not in CONVERSION_RATES:
            raise ValidationError(f"Taux indisponible pour : {source_currency}")
        if target_currency not in CONVERSION_RATES[source_currency]:
            raise ValidationError(f"Taux indisponible pour : {target_currency}")
        rate = Decimal(str(CONVERSION_RATES[source_currency][target_currency]))
        return amount * rate

    def __str__(self):
        return f"{self.user.username} - {self.balance} {self.currency}"

    def populate_wallet(self):
        self.balance = Decimal("10000.00")
        self.currency = CurrencyChoices.USD
        print(f"[WALLET INIT] Balance: {self.balance}")
        self.save()


class Transaction(TimeAbstractModel):

    id = models.AutoField(primary_key=True)
    sender_wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="sent_transactions"
    )
    receiver_wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="received_transactions"
    )
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    scheduled = models.DateTimeField(null=True, blank=True)
    event = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=TransactionStatusChoices.choices)

    class Meta:
        app_label = "transfer_currency"

    def clean(self):
        try:
            sender_wallet = self.sender_wallet
        except self.__class__.sender_wallet.RelatedObjectDoesNotExist:
            sender_wallet = None

        try:
            receiver_wallet = self.receiver_wallet
        except self.__class__.receiver_wallet.RelatedObjectDoesNotExist:
            receiver_wallet = None

        if self.amount is not None and self.amount <= 0:
            raise ValidationError("Le montant doit être supérieur à zéro.")

        if sender_wallet and receiver_wallet:
            if sender_wallet == receiver_wallet:
                raise ValidationError(
                    "Le portefeuille source et le portefeuille cible doivent être différents."
                )
            if sender_wallet.balance < self.amount:
                raise ValidationError("Fonds insuffisants sur le portefeuille source.")

    def __str__(self):
        return f"{self.amount} {self.sender_wallet.currency} - {self.status}"

    def to_entity(self) -> TransactionEntity:
        return TransactionEntity(
            id=self.id,
            sender_wallet_id=self.sender_wallet.id,
            receiver_wallet_id=self.receiver_wallet.id,
            amount=float(self.amount),
            created_at=self.created_at,
            scheduled=self.scheduled,
            event=self.event,
            status=self.status,
        )

    @property
    def status_display(self):
        return TransactionStatusChoices(self.status).label


class Notification(TimeAbstractModel):
    class Meta:
        app_label = "transfer_currency"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"To {self.user.username}: {self.message}"
