from django.urls import path
from .views import register_view_test, login_view
from django.contrib.auth import views as auth_views
app_name = 'accounts'
urlpatterns = [
    path('test-form/', register_view_test, name='test_form'),
    path('login/', login_view, name='login'),

]