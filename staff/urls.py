from django.urls import path
from .views import staff_dashboard_view, staff_contact_messages_list_view, staff_orders_list_view, notifications_view, \
    staff_order_detail_view, notification_is_read_view, reviews_view, review_approve_view

app_name = 'staff'
urlpatterns = [
    path('staff-dashboard/', staff_dashboard_view, name='staff_dashboard'),
    path('staff-contact-messages/', staff_contact_messages_list_view, name='staff_contact_messages'),
    path('staff-orders/', staff_orders_list_view, name='staff_orders_list'),
    path('staff-order-detail/<int:order_id>/', staff_order_detail_view, name='staff_order_detail'),
    path('staff-notifications/', notifications_view, name='staff_notifications'),
    path('staff-notification/<int:notification_id>/read/', notification_is_read_view, name='staff_notification_read'),
    path('staff-reviews/',reviews_view,name='staff_reviews_list'),
    path('staff-review-approve/<int:review_id>/',review_approve_view,name='staff_approve_review'),


]
