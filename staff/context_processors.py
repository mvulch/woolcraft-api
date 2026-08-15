from .models import NotificationRecipient

def staff_notification_count(request):
    if request.user.is_authenticated and request.user.is_staff:
        count = NotificationRecipient.objects.filter(recipient=request.user,is_read=False).count()
        return { 'staff_notification_count': count }
    return { 'staff_notification_count': 0 }