import copy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView
from django.views.generic.detail import DetailView
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.accounts.infrastructure.models import User


from apps.transfer_currency.interfaces.forms import (
    CustomUserCreationForm,
    ImmediateTransferForm,
    ScheduledTransferForm,
    WalletCreationForm,
)
from apps.transfer_currency.infrastructure.models import (
    Notification,
    Transaction,
    Wallet,
    TransactionStatusChoices,
)
from apps.transfer_currency.interfaces.serializers import (
    NotificationSerializer,
    TransactionSerializer,
    UserSerializer,
    WalletSerializer,
)
from apps.transfer_currency.interfaces.utilis.email_utilis import send_transfer_email
from apps.transfer_currency.tasks import notify_sender, notify_receiver


class HomeView(TemplateView):
    template_name = "home.html"


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "register.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        user = form.save()
        currency = form.cleaned_data.get("currency", "USD")
        Wallet.objects.create(user=user, balance=5000, currency=currency)
        login(self.request, user)
        return redirect("dashboard")


class LoginView(LoginView):
    template_name = "login.html"
    next_page = reverse_lazy("dashboard")


class LogoutView(LogoutView):
    next_page = reverse_lazy("home")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        wallet = get_object_or_404(Wallet, user=user)
        context["wallet"] = wallet

        context["transactions"] = Transaction.objects.filter(
            sender_wallet=wallet
        ).order_by("-created_at")

        context["scheduled_transfers"] = Transaction.objects.filter(
            sender_wallet=wallet,
            status="scheduled",
            scheduled__gt=timezone.now(),
        ).order_by("-created_at")

        context["unread_notifications"] = Notification.objects.filter(
            user=user, is_read=False
        ).count()

        return context


class ImmediateTransferView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = ImmediateTransferForm
    template_name = "create_transfer.html"
    success_url = reverse_lazy("dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        user_wallet = get_object_or_404(Wallet, user=self.request.user)
        receiver_user = form.cleaned_data["receiver_username"]
        receiver_wallet = get_object_or_404(Wallet, user=receiver_user)

        transaction = form.save(commit=False)
        transaction.sender_wallet = user_wallet
        transaction.receiver_wallet = receiver_wallet
        transaction.status = "completed"
        transaction.event = form.cleaned_data.get("event")

        amount = form.cleaned_data.get("amount")
        if amount > user_wallet.balance:
            form.add_error("amount", "Insufficient balance.")
            return self.form_invalid(form)

        user_wallet.balance -= amount
        converted_amount = Wallet.get_converted_amount(
            amount,
            receiver_wallet.currency,
            user_wallet.currency,
        )
        receiver_wallet.balance += converted_amount

        user_wallet.save()
        receiver_wallet.save()
        transaction.save()

        Notification.objects.create(
            user=receiver_wallet.user,
            message=(
                f"You received {converted_amount} {receiver_wallet.currency} "
                f"from {user_wallet.user.username}."
            ),
        )

        try:
            send_transfer_email(
                receiver=receiver_user,
                sender=self.request.user,
                amount=converted_amount,
                currency=receiver_wallet.currency,
                event=transaction.event,
                success=True,
            )
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")

        return super().form_valid(form)

    def process_transfer(sender, receiver, amount):

        notify_sender.delay(sender.email, amount, receiver.username)
        notify_receiver.delay(receiver.email, amount, sender.username)


class ScheduleTransferView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = ScheduledTransferForm
    template_name = "schedule_transfer.html"
    success_url = reverse_lazy("dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        sender_wallet = get_object_or_404(Wallet, user=self.request.user)
        receiver_user = form.cleaned_data.get("receiver_username")
        try:
            receiver_wallet = Wallet.objects.get(user=receiver_user)
        except Wallet.DoesNotExist:
            form.add_error("receiver_username", "Recipient does not have a wallet.")
            return self.form_invalid(form)

        amount = form.cleaned_data.get("amount")
        if amount <= 0:
            form.add_error("amount", "Amount must be greater than 0.")
            return self.form_invalid(form)

        transaction = form.save(commit=False)
        transaction.sender_wallet = sender_wallet
        transaction.receiver_wallet = receiver_wallet
        transaction.status = "scheduled"
        transaction.save()
        return super().form_valid(form)


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = "transaction_details.html"
    context_object_name = "transaction"

    def get_queryset(self):
        return Transaction.objects.filter(sender_wallet__user=self.request.user)


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications.html"
    context_object_name = "notifications"
    ordering = ["-created_at"]

    def get_queryset(self):
        nots = self.request.user.notifications.all().order_by("-created_at")
        nots_copy = copy.deepcopy(list(nots))
        nots.update(is_read=True)
        return nots_copy


class CancelScheduledTransferView(LoginRequiredMixin, View):
    def post(self, request, pk):
        tran = get_object_or_404(Transaction, pk=pk, sender_wallet__user=request.user)
        if tran.status == TransactionStatusChoices.SCHEDULED:
            tran.status = (
                TransactionStatusChoices.FAILED
            )  # ou un autre statut selon ton intention

        return redirect("dashboard")


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response(
                {
                    "message": "Logged in successfully.",
                    "user": UserSerializer(user).data,
                }
            )
        return Response(
            {"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
        )

    @action(detail=False, methods=["post"])
    def logout(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."})


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        currency = serializer.validated_data.get("currency")
        if Wallet.objects.filter(user=self.request.user, currency=currency).exists():
            raise ValidationError("Vous avez déjà un portefeuille dans cette devise.")
        serializer.save(user=self.request.user)


class WalletCreateView(LoginRequiredMixin, CreateView):
    model = Wallet
    form_class = WalletCreationForm
    template_name = "create_wallet.html"
    success_url = reverse_lazy("dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "notification marked as read"})
