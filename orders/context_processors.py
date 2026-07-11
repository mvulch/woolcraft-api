from django.db import models

from .models import Cart


def cart_item_count(request):
    count = request.session.get('cart_item_count', 0)
    """
    count = 0
    if request.user.is_authenticated:
        cart = getattr(request.user, 'cart', None)
    else:
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_key=session_key).first()
        else:
            cart = None
    if cart:
        count = cart.item.aggregate(total=models.Sum('quantity'))['total']
    return {'cart_item_count': count}
    """
    return {'cart_item_count': count}