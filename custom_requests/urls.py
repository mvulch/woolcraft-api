from django.urls import path
from .views import custom_request_create_view, custom_requests_list_view, custom_request_detail_view
app_name = 'custom_requests'
urlpatterns = [
    path('custom-request-create',custom_request_create_view, name='custom_request_create'),
    path('custom-request-detail/<int:request_id>/', custom_request_detail_view, name='custom_request_detail'),
    path('custom-requests-list', custom_requests_list_view, name='custom_requests_list'),

]