from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Cart, CartItem, Address
from django.contrib import messages
from .utils import update_cart_count
from products.models import Product
from .forms import AddressForm

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

@login_required
def address_list_view(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'orders/address_list.html', {'addresses': addresses})

@login_required
def address_create_view(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if not Address.objects.filter(user=request.user).exists():
                address.is_default = True
            address.save()
            messages.success(request, "Адресът беше запазен.")
            return redirect('orders:address_list')
    else:
        form = AddressForm()
    return render(request, 'orders/address_form.html',{'form': form, 'title': 'Нов адрес'})

@login_required
def address_edit_view(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        print("debug: address_edit_view - is in post")
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Адресът беше обновен успешно.")
            return redirect('orders:address_list')
    else:
        form = AddressForm(instance=address)
    return render(request, 'orders/address_form.html', {'form': form,  'title': 'Редактирай адрес'})


@login_required
def address_delete_view(request, address_id):
    address = get_object_or_404(Address, id=address_id,user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, "Адресът беше премахнат успешно.")
    return redirect('orders:address_list')

@login_required
def address_set_default_view(request, address_id):
    address = get_object_or_404(Address, id=address_id,user=request.user)
    Address.objects.filter(user=request.user).update(is_default=False)
    address.is_default=True
    address.save()
    return redirect('orders:address_list')