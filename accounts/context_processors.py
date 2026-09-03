from .forms import LoginForm
from .models import UserNotification

def login_credentials(request):
    if request.user.is_authenticated:
        return {}
    return {'form': LoginForm()}

def user_notification_count(request):
    if request.user.is_authenticated and not request.user.is_staff:
        count = UserNotification.objects.filter(recipient=request.user,is_read=False).count()
        return { 'user_notification_count': count }
    return { 'user_notification_count': 0 }