from django.db import models
from django.db.models import F
from django.conf import settings
from products.models import Product

# Create your models here.
class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name="addresses")
    first_name = models.CharField(max_length=25,blank=False)
    last_name = models.CharField(max_length=30,blank=False)
    phone = models.CharField(max_length=15,blank=False)
    street = models.CharField(max_length=50,blank=False)
    city = models.CharField(max_length=30,blank=False)
    postal_code = models.CharField(max_length=10,blank=False)
    country = models.CharField(max_length=30,blank=False)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреси"

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
    class Meta:
        verbose_name = "Количка"
        verbose_name_plural = "Колички"
    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"
        return f"Cart of session {self.session_key}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="item")
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True, related_name="cart_items")
    quantity = models.PositiveIntegerField(blank=False, default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def get_subtotal(self):
        if self.product:
            return self.product.price * self.quantity
        return 0
    class Meta:
        unique_together = ('cart', 'product')
        verbose_name = "Артикул в количка"
        verbose_name_plural = "Артикули в колички"

    def __str__(self):
        return f"{self.quantity} x {self.product} from {self.cart}"

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PAID = "PAID", "Платена"
        SHIPPED = "SHIPPED", "Изпратена"
        DELIVERED = "DELIVERED", "Доставена"
        CANCELLED = "CANCELLED", "Отказана"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="orders")
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    status = models.CharField(max_length=15,choices=OrderStatus.choices,default=OrderStatus.PAID)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stripe_payment_id = models.CharField(max_length=200, blank=True, unique=True)
    #stripe_customer_id
    class Meta:
        verbose_name = "Поръчка"
        verbose_name_plural = "Поръчки"

    def restock_items(self):
        for item in self.items.all():
            if item.product_id:
                Product.objects.filter(id=item.product_id).update(
                    stock_quantity=F('stock_quantity') + item.quantity
                )
    def __str__(self):
        return f"Order #{self.id} of {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete = models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete = models.SET_NULL, null=True, related_name="order_items")
    quantity = models.PositiveIntegerField(blank=False)
    price_at_purchase = models.DecimalField(max_digits=15, decimal_places=2)

    def get_subtotal(self):
        return self.price_at_purchase * self.quantity
    class Meta:
        verbose_name = "Артикул в поръчка"
        verbose_name_plural = "Артикули в поръчки"
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
        verbose_name = "История на статус на поръчка"
        verbose_name_plural = "История на статус на поръчки"
    def __str__(self):
        return f"{self.order}: {self.old_status} -> {self.new_status}"
