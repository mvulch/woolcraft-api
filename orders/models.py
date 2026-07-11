from django.db import models
from django.conf import settings

from products.models import Product


# Create your models here.
class Address(models.Model):
    class Types(models.TextChoices):
        SHIPPING = "SHIPPING", "Shipping"
        INVOICING = "INVOICING", "Invoicing"

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name="addresses")
    first_name = models.CharField(max_length=25,blank=False)
    last_name = models.CharField(max_length=30,blank=False)
    phone = models.CharField(max_length=15,blank=False)
    street = models.CharField(max_length=50,blank=False)
    city = models.CharField(max_length=30,blank=False)
    postal_code = models.CharField(max_length=10,blank=False)
    country = models.CharField(max_length=30,blank=False)
    address_type = models.CharField(max_length=20, choices=Types.choices, default=Types.SHIPPING)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "address"
        verbose_name_plural = "addresses"

    def __str__(self):
        return f"{self.street} {self.city} {self.country}"


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name = "cart", null=True, blank=True)
    session_key = models.CharField(max_length=40,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total(self):
        return sum(item.get_subtotal() for item in self.item.all())
    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"
        return f"Cart of session {self.session_key}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="item")
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    quantity = models.PositiveIntegerField(blank=False, default=1)
    added_at = models.DateTimeField(auto_now_add=True)


    def get_subtotal(self):
        return self.product.price * self.quantity
    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product} from {self.cart}"

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="orders")
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    status = models.CharField(max_length=15,choices=OrderStatus.choices,default=OrderStatus.PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #stripe_payment_id
    #stripe_customer_id

    def __str__(self):
        return f"Order #{self.id} of {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete = models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(blank=False)
    price_at_purchase = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product} from {self.order}"

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_status_history")
    old_status = models.CharField(max_length=15, choices=Order.OrderStatus.choices)
    new_status = models.CharField(max_length=15, choices=Order.OrderStatus.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    changed_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length = 200, blank=True)

    class Meta:
        verbose_name = "orderStatusHistory"
        verbose_name_plural = "orderStatusHistory"

    def __str__(self):
        return f"{self.order}: {self.old_status} -> {self.new_status}"
