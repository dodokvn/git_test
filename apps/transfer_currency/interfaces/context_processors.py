from apps.transfer_currency.infrastructure.models import Notification


def unread_notifications(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        count = 0
    return {"unread_notifications": count}


def global_context(request):
    context = {}
    if request.user.is_authenticated:
        context["unread_notifications"] = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        # Tu peux ajouter plus de données ici
    return context
