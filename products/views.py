from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.core.paginator import Paginator

# Create your views here.
def home_view(request):
    latest_products = Product.objects.filter(is_active=True).order_by('created_at').prefetch_related('images')[:5]
    return render(request, 'home.html', {'latest_products': latest_products})

def product_detail_view(request,category_slug,slug):
    product_detail = get_object_or_404(Product.objects
                                       .select_related('category','video_course')
                                       .prefetch_related('attributes', 'images'), is_active=True,slug=slug, category__slug=category_slug)
    return render(request, 'products/product_detail.html', {'product': product_detail})

def category_products_view(request, category_slug=None):
    # all main categories
    categories = Category.objects.filter(parent=None).prefetch_related('subcategories')
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('attributes', 'images')
    category=None
    if category_slug:
        # the chosen category at the moment
        category = get_object_or_404(Category,slug=category_slug)
        subcategory_id = category.subcategories.values('id')
        products = products.filter(Q(category=category) | Q(category_id__in=subcategory_id))
    paginator = Paginator(products, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'categories': categories,
        #'products': products,
        'page_obj': page_obj
    }
    return render(request, 'products/category_products.html', context)
