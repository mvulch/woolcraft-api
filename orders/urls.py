from django.urls import path
from .views import create_and_add_cart_view, cart_detail_view, remove_from_cart_view,update_cart_view

app_name = 'orders'
urlpatterns = [
    path('add-to-cart/<int:product_id>/', create_and_add_cart_view, name='add_to_cart'),
    path('cart', cart_detail_view, name='cart_detail'),
    path('remove-from-cart/<int:cart_item_id>/', remove_from_cart_view, name='remove_from_cart'),
    path('update-cart/<int:cart_item_id>/', update_cart_view, name='update_cart'),
]