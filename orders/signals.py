from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from orders.models import Cart, CartItem
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger(__name__)
# hours the users cart stays before being replaced by an anonymous cart
STALE_CART_AFTER = timedelta(hours=48)

@receiver(user_logged_in)
def transfer_or_merge_cart(sender, request, user, **kwargs):
    session_key = request.session.get('_old_session_key')
    #print(f"debug: old sessionkey = {session_key}")
    if not session_key:
        return

    anonym_cart = Cart.objects.filter(session_key=session_key, user=None).first()
    #print(f"debug: anonym cart = {anonym_cart}")
    if not anonym_cart:
        return

    with transaction.atomic():
        logged_cart = Cart.objects.filter(user=user).first()
        # user didnt have a cart
        if not logged_cart:
            anonym_cart.user = user
            anonym_cart.session_key = None
            anonym_cart.save()
            return
        # user had a cart
        else:
            time_threshold = timezone.now() - STALE_CART_AFTER
            #print(f"debug: time threshold = {time_threshold}")
            #print(f"debug: is old == {logged_cart.updated_at < time_threshold}")
            # in case of an old cart in the profile:
            last_item = logged_cart.item.order_by('-added_at').first()
            #if logged_cart.updated_at < time_threshold:
            if not last_item or last_item.added_at < time_threshold:
                logged_cart.delete()
                anonym_cart.user = user
                anonym_cart.session_key = None
                anonym_cart.save()
                return
            # the cards should merge
            for anonym_item in anonym_cart.item.all():
                if anonym_item.product is None:
                    continue
                cart_item, item_created = CartItem.objects.get_or_create(
                    cart=logged_cart,
                    product=anonym_item.product,
                    defaults={'quantity': anonym_item.quantity}
                )
                if not item_created:
                    new_quantity = cart_item.quantity + anonym_item.quantity
                    cart_item.quantity = min(new_quantity, anonym_item.product.stock_quantity)
                    cart_item.save()
            anonym_cart.delete()
            logger.debug('Merged anonymous cart %s into cart %s for user %s',
                     session_key, logged_cart.id, user.pk)
