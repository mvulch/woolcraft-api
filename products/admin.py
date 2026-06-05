from django.contrib import admin
from .models import Category, Product, ProductAttribute, ProductImage,VideoCourse
# Register your models here.
"""admin.site.register(Category)
    admin.site.register(Product)
    admin.site.register(ProductAttribute)
    admin.site.register(ProductImage)
    admin.site.register(VideoCourse)"""
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug")
    search_fields =("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name","category", "price", "stock_quantity", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active", "category")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "value")
    search_fields = ("product__name", "name")

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "is_primary", "alt_text")
    list_filter = ("is_primary",)

@admin.register(VideoCourse)
class VideoCourseAdmin(admin.ModelAdmin):
    list_display = ("product", "duration_minutes", "difficulty")
    list_filter = ("difficulty",)

