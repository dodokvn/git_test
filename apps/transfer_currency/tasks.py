from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now,make_aware
from apps.accounts.infrastructure.models import User
from apps.transfer_currency.infrastructure.models import Wallet
from django_celery_beat.models import PeriodicTask,ClockedSchedule 
import json

@shared_task
def notify_sender(user_email, amount, recipient_name):
    send_mail(
        "money sent",
        f"you{amount}to {recipient_name}at {now()}",
        "no-reply@yourapp.com",
        [user_email],
    )


@shared_task
def notify_receiver(receiver_email, amount, sender_name):
    send_mail(
        "money received",
        f"you received{amount}from{sender_name}at{now()}",
        "no-reply@yourapp.com",
        [receiver_email],
    )


@shared_task
def execute_scheduled_transfer(send_id, receiver_id, amount):

    sender = User.objects.get(id=send_id)
    receiver = User.objects.get(id=receiver_id)

    notify_sender.delay(sender.email, amount, receiver.username)
    notify_receiver.delay(receiver.email, amount, sender.username)

def schedule_transfer(sender,receiver,amount,schedule_datetime):
    clocked_time = make_aware(schedule_datetime)
    clocked,_ = ClockedSchedule.objects.get_or_create(clocked_time=clocked_time)

    PeriodicTask.objects.create(
        clocked=clocked,name =f'transfer{sender.id}{receiver.id}{clocked_time}'
        task='apps.transfer_currency.tasks.execute_scheduled_transfer'
        one_off=True,
        args = json.dumps([sender.id,receiver.id,str(amount)])
        )

