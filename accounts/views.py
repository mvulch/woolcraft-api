from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView, LogoutView
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import RegistrationForm, LoginForm
from .models import UserNotification

# Create your views here.
def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            first_name = form.cleaned_data.get('first_name')
            messages.success(request, f"{first_name}, регистрацията е успешна. Влезте в профила си.")
            return redirect('accounts:login')
    else:
        form = RegistrationForm()
        #print(form.errors)

    return render(request, "accounts/registration.html",{'form':form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
        # return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None:
                request.session['_old_session_key'] = request.session.session_key
                login(request, user)
                request.session.pop('cart_item_count', None)
                # return redirect('accounts:profile')
                return redirect('home')
            else:
                messages.error(request, "Грешен имейл или парола.")
        else:
            messages.error(request, "Невалиден формат на данни. Моля, опитайте отново.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form':form})

@login_required
def profile_view(request):
    print(f"Context user is: {request.user}")
    return render(request, 'accounts/profile.html', {'user': request.user})

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')

class CustomLogoutView(LogoutView):
    next_page = 'home'

@login_required
def user_notifications_view(request):
    filter_read = request.GET.get('read', '')
    filter_type = request.GET.get('type', '')
    notifications = UserNotification.objects.filter(recipient=request.user)
    if filter_type:
        notifications = notifications.filter(type=filter_type)
    if filter_read == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_read == 'read':
        notifications = notifications.filter(is_read=True)
    paginator = Paginator(notifications, 2)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'page_obj': page_obj,
        'type_choices': UserNotification.Type.choices,
        'current_type': filter_type,
        'current_read': filter_read,
    }
    return render(request, 'accounts/notifications.html', context)

@login_required
def user_notification_is_read_view(request, notification_id):
    notification = get_object_or_404(UserNotification, id=notification_id, recipient=request.user)
    notification.is_read=True
    notification.save()
    if notification.link:
        return redirect(notification.link)
    return redirect('accounts:notifications')