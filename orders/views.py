from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Cart, CartItem
from django.contrib import messages
from .utils import update_cart_count
from products.models import Product

@require_POST
def create_and_add_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    requested_quantity = int(request.POST.get('quantity', 1))
    if request.user.is_authenticated:
        cart, cart_created = Cart.objects.get_or_create(user=request.user)
        # no sessionkey param in case of an anonymous user who authenticates later
    else:
        if not request.session.session_key:
            request.session.create()
        print(f"add  to cart: session key = {request.session.session_key}")
        cart, cart_created = Cart.objects.get_or_create(session_key=request.session.session_key)

    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity':0})

    new_quantity= cart_item.quantity + requested_quantity
    print(f"DEBUG: new_quantity = {new_quantity}")
    print(f"DEBUG: cart_item.quantity = {cart_item.quantity}")
    print(f"DEBUG: requested_quantity = {requested_quantity}")
    if new_quantity > product.stock_quantity:
        messages.warning(request,f"Недостатъчна наличност от артикул {product.name} - "
                                 f"брой налични продукти в магазина: {product.stock_quantity} - брой продукти във вашата кошница: {cart_item.quantity}")
    else:
        cart_item.quantity = new_quantity
        cart_item.save()
        print(f"DEBUG: updating count, cart={cart.id}")
        update_cart_count(request, cart)
        messages.success(request, f"Артикул {product.name} беше добавен в количката.")

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('products:all_products')

def cart_detail_view(request):
    cart = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).prefetch_related('item__product__images').first()
    else:
        session_key = request.session.session_key
        if not session_key:
            return render(request, 'orders/cart_detail.html', {'cart': None, 'items': []})

        cart = Cart.objects.filter(session_key=request.session.session_key).prefetch_related('item__product__images').first()
    if cart:
        items = cart.item.all()
        update_cart_count(request, cart)
    else:
        items = []
    context = {
        'cart': cart,
        'items': items
    }
    return render(request, 'orders/cart_detail.html', context)

@require_POST
def remove_from_cart_view(request, cart_item_id):
    cart_item = get_object_or_404(CartItem.objects.select_related('cart'), id=cart_item_id)
    if cart_item.cart.user == request.user or cart_item.cart.session_key == request.session.session_key:
        cart_item.delete()
    return redirect('orders:cart_detail')

@require_POST
def update_cart_view(request, cart_item_id):
    cart_item = get_object_or_404(CartItem.objects.select_related('cart'), id=cart_item_id)
    action = request.POST.get('action')
    if cart_item.cart.user == request.user or cart_item.cart.session_key == request.session.session_key:
        if action == 'increase':
            if cart_item.product.stock_quantity > cart_item.quantity:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.warning(request,
                                f"Достигната е максималната наличност от {cart_item.product.name}.")
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        update_cart_count(request,cart_item.cart)
    return redirect('orders:cart_detail')
