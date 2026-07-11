from django.db.models import Sum

def update_cart_count(request, cart):
    count = cart.item.aggregate(total=Sum('quantity'))['total'] or 0
    request.session['cart_item_count'] = count