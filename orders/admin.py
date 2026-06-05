from django.contrib import admin
from .models import Address, Cart, CartItem, Order, OrderItem, OrderStatusHistory
# Register your models here.

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user","street", "city", "country", "address_type")
    search_fields = ("city", "country", "user__email")
    list_filter = ("address_type", "is_default")
    readonly_fields = ("created_at",)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user","session_key","created_at","updated_at")
    search_fields = ("user__email",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "added_at")
    search_fields = ("product__name",)
    readonly_fields = ("added_at",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "address", "total_price","status","created_at")
    search_fields = ("address__city","address__country","user__email")
    list_filter = ("status",)
    readonly_fields = ("created_at",)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price_at_purchase")
    search_fields = ("product__name",)
    readonly_fields = ("price_at_purchase",)

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("order", "old_status", "new_status", "changed_by", "changed_at")
    search_fields = ("changed_by__email",)
    list_filter = ("old_status", "new_status")
    readonly_fields = ("changed_at",)

