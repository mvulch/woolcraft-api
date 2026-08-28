from django.db import models
from .models import Cart


def cart_item_count(request):
    count = request.session.get('cart_item_count')
    print(f"DEBUG: COUNT FROM SESSION = {count}")
    if count is None or (request.user.is_authenticated and count == 0):
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
            print(f"DEBUG: authenticated, cart = {cart}")
        else:
            session_key = request.session.session_key
            print(f"DEBUG: anonym, session key = {session_key}")
            if session_key:
                cart = Cart.objects.filter(session_key=session_key).first()
                print(f"DEBUG: if session key TRUE")
            else:
                cart = None
                print(f"DEBUG: if session key FALSE")
        if cart:
            count = cart.item.aggregate(total=models.Sum('quantity'))['total'] or 0
            print(f"DEBUG: ccount from db = {count}")
        else:
            count = 0
        request.session['cart_item_count'] = count

    return {'cart_item_count': count}