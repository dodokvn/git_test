# utils/email_utils.py

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_transfer_email(receiver, sender, amount, currency, event, success=True):
    print(receiver)
    subject = (
        "You have received a scheduled money transfer"
        if success
        else "Scheduled transfer failed"
    )
    to_email = receiver.email if success else sender.email

    context = {
        "receiver": receiver,
        "sender": sender,
        "amount": amount,
        "currency": currency,
        "event": event,
        "success": success,
    }

    html_content = render_to_string("emails/transfer_notification.html", context)
    text_content = f"""
    {'You have received' if success else 'Your scheduled transfer failed'}:
    {amount} {currency} {'from' if success else 'to'} {sender.username if success else receiver.username}.
    Reason: {event}.
    """

    email = EmailMultiAlternatives(
        subject, text_content, settings.DEFAULT_FROM_EMAIL, [to_email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
