from django.urls import path
from .views import product_detail_view, category_products_view, quick_view

app_name = 'products'
urlpatterns = [
    path('',  category_products_view, name='all_products'),
    path('quick-view/<int:product_id>/', quick_view, name='quick_view'),
    path('<slug:category_slug>/<slug:slug>/', product_detail_view, name='product_detail'),
    path('<slug:category_slug>/', category_products_view, name='category_products'),


]