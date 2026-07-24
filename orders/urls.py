from django.urls import path
from .views import (create_and_add_cart_view, cart_detail_view, remove_from_cart_view, update_cart_view,
                    address_list_view, address_create_view, address_edit_view, address_delete_view, address_set_default_view)

app_name = 'orders'
urlpatterns = [
    path('add-to-cart/<int:product_id>/', create_and_add_cart_view, name='add_to_cart'),
    path('cart', cart_detail_view, name='cart_detail'),
    path('remove-from-cart/<int:cart_item_id>/', remove_from_cart_view, name='remove_from_cart'),
    path('update-cart/<int:cart_item_id>/', update_cart_view, name='update_cart'),
    path('address-list', address_list_view, name='address_list'),
    path('address-create', address_create_view, name='address_create'),
    path('address-edit/<int:address_id>/', address_edit_view, name='address_edit'),
    path('address-delete/<int:address_id>/', address_delete_view, name='address_delete'),
    path('address-set-default/<int:address_id>/', address_set_default_view, name='address_set_default')
]