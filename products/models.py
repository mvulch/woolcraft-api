from django.db import models
from django.conf import settings

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=120, blank=False,unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    slug = models.SlugField(max_length=100, blank=False,unique=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True,related_name="subcategories")

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=120, blank=False)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_products")
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=False)
    slug = models.SlugField(max_length=100, blank=False,unique=True)

    def get_quantity_range(self):
        return range(1, self.stock_quantity + 1)
    def get_main_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукти'

class ProductAttribute(models.Model):
    product = models.ForeignKey(Product,on_delete = models.CASCADE,related_name="attributes")
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"
    class Meta:
        verbose_name = 'Атрибут на продукт'
        verbose_name_plural = 'Атрибути на продукти'

class ProductImage(models.Model):
    product = models.ForeignKey(Product,on_delete = models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=120, blank=True)
    class Meta:
        verbose_name = 'Изображение за продукт'
        verbose_name_plural = 'Изображения за продукти'
    def __str__(self):
        return f"Image for {self.product.name}"

class ProductReview(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    class Meta:
        unique_together = ('user','product')
        ordering = ['-created_at']
        verbose_name = 'Ревю на продукт'
        verbose_name_plural = 'Ревюта на продукти'
    def __str__(self):
        return f'Review of {self.product.name} from {self.user.email}'

class VideoCourse(models.Model):

    class Difficulty(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name = "video_course")
    video_url = models.URLField(max_length=500, blank=False)
    duration_minutes = models.PositiveIntegerField(blank=False)
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices,default=Difficulty.BEGINNER)

    def __str__(self):
        return self.product.name
    class Meta:
        verbose_name = 'Видео курс'
        verbose_name_plural = 'Видео курсове'
