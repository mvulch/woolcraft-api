from django.urls import path
from .views import (create_and_add_cart_view, cart_detail_view, remove_from_cart_view, update_cart_view,
                    address_list_view, address_create_view, address_edit_view, address_delete_view,
                    address_set_default_view,
                    order_detail_view, check_out_view, order_list_view,
                    payment_success_view, create_checkout_session, stripe_webhook)

app_name = 'orders'
urlpatterns = [
    path('add-to-cart/<int:product_id>/', create_and_add_cart_view, name='add_to_cart'),
    path('cart/', cart_detail_view, name='cart_detail'),
    path('remove-from-cart/<int:cart_item_id>/', remove_from_cart_view, name='remove_from_cart'),
    path('update-cart/<int:cart_item_id>/', update_cart_view, name='update_cart'),
    path('address-list/', address_list_view, name='address_list'),
    path('address-create/', address_create_view, name='address_create'),
    path('address-edit/<int:address_id>/', address_edit_view, name='address_edit'),
    path('address-delete/<int:address_id>/', address_delete_view, name='address_delete'),
    path('address-set-default/<int:address_id>/', address_set_default_view, name='address_set_default'),
    path('check-out/', check_out_view, name='check_out'),
    path('order-detail/<int:order_id>', order_detail_view, name='order_detail'),
    path('order-list',order_list_view, name='order_list'),
    path('create-checkout-session/<int:order_id>', create_checkout_session, name='create_checkout_session'),
    path('payment-success/',payment_success_view, name='payment_success'),
    path('stripe-webhook/',stripe_webhook, name='stripe_webhook'),

]