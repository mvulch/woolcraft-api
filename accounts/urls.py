from django.urls import path
from .views import register_view, login_view, profile_view, CustomPasswordChangeView, CustomLogoutView
from django.contrib.auth import views as auth_views

app_name = 'accounts'
urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('profile/', profile_view, name='profile'),
    path('password-change/', CustomPasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('logout', CustomLogoutView.as_view(), name='logout'),

]