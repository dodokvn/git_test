from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms.widgets import DateTimeInput
from django.utils import timezone

from transfer_currency.infrastructure.models import (
    CURRENCY_CHOICES,
    Transaction,
    User,
    Wallet,
)


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-input rounded-md border-gray-300 shadow-sm",
                "placeholder": "Enter your email",
            }
        ),
    )

    currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone_number",
            "password1",
            "password2",
        ]
        widgets = {
            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-input rounded-md border-gray-300 shadow-sm",
                    "placeholder": "Enter your phone number",
                }
            ),
            "password1": forms.PasswordInput(
                attrs={"class": "form-input rounded-md border-gray-300 shadow-sm"}
            ),
            "password2": forms.PasswordInput(
                attrs={"class": "form-input rounded-md border-gray-300 shadow-sm"}
            ),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if User.objects.filter(phone_number=phone).exists():
            raise ValidationError("This phone number is already registered.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email


class WalletCreationForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ["currency"]
        widgets = {"currency": forms.Select(attrs={"class": "form-select"})}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        currency = cleaned_data.get("currency")
        user = self.user or self.instance.user

        if Wallet.objects.filter(user=user, currency=currency).exists():
            raise ValidationError("Vous avez déjà un portefeuille dans cette devise.")
        return cleaned_data

    def save(self, commit=True):
        wallet = super().save(commit=False)
        wallet.user = self.user
        wallet.balance = 5000  # Solde initial
        if commit:
            wallet.save()
        return wallet


class BaseTransferForm(forms.ModelForm):
    receiver_username = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Recipient",
        widget=forms.Select(
            attrs={"class": "form-input rounded-md border-gray-300 shadow-sm"}
        ),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["receiver_username"].queryset = User.objects.exclude(
            id=self.user.id
        ).exclude(is_superuser=True)

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get("amount")

        if amount is None:
            return cleaned_data

        if amount <= 0:
            raise ValidationError("The amount must be greater than 0.")

        if amount > 5_000_000:
            raise ValidationError("Transfer amount cannot exceed 5 million.")

        try:
            Wallet.objects.get(user=self.user)
        except Wallet.DoesNotExist:
            raise ValidationError(
                "You do not have a wallet to perform this transaction."
            )

        today = timezone.now().date()
        start_of_day = timezone.make_aware(
            timezone.datetime.combine(today, timezone.datetime.min.time())
        )
        end_of_day = timezone.make_aware(
            timezone.datetime.combine(today, timezone.datetime.max.time())
        )

        daily_transactions = Transaction.objects.filter(
            sender_wallet__user=self.user,
            timestamp__range=(start_of_day, end_of_day),
        )

        total_daily_amount = sum(tx.amount for tx in daily_transactions)

        if total_daily_amount + amount > 30_000_000:
            raise ValidationError("Total daily transfers cannot exceed 30 million.")

        return cleaned_data


class ImmediateTransferForm(BaseTransferForm):
    class Meta:
        model = Transaction
        fields = ["receiver_username", "amount", "event"]
        widgets = {
            "amount": forms.NumberInput(
                attrs={"class": "form-input rounded-md border-gray-300 shadow-sm"}
            ),
            "event": forms.TextInput(
                attrs={
                    "class": "form-input rounded-md border-gray-300 shadow-sm",
                    "placeholder": "e.g. Gift, payment, etc.",
                }
            ),
        }


class ScheduledTransferForm(BaseTransferForm):
    scheduled = forms.DateTimeField(
        widget=DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-input rounded-md border-gray-300 shadow-sm",
                "id": "local_datetime",
            }
        ),
        label="Schedule for",
    )

    class Meta:
        model = Transaction
        fields = ["receiver_username", "amount", "scheduled", "event"]
        widgets = {
            "amount": forms.NumberInput(
                attrs={"class": "form-input rounded-md border-gray-300 shadow-sm"}
            ),
            "event": forms.TextInput(
                attrs={
                    "class": "form-input rounded-md border-gray-300 shadow-sm",
                    "placeholder": "e.g. Rent, subscription, etc.",
                }
            ),
        }

    def clean_scheduled(self):
        scheduled = self.cleaned_data.get("scheduled")
        if scheduled and scheduled < timezone.now():
            raise ValidationError("Scheduled time cannot be in the past.")
        return scheduled
