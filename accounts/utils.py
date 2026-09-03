from .models import UserNotification

def notify_user(user, type, message, link=''):
    UserNotification.objects.create(recipient=user, type=type, message=message,link=link,)
