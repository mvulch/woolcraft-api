from django.db.models import Sum
from staff.utils import notify_staff
from staff.models import Notification
import json, logging
import stripe
from django.db import transaction
from .models import Address, Cart, Order, OrderItem
from products.models import Product

logger = logging.getLogger(__name__)

def update_cart_count(request, cart):
    count = cart.item.aggregate(total=Sum('quantity'))['total'] or 0
    request.session['cart_item_count'] = count

ORDER_TIMELINE_STEPS = (
    (Order.OrderStatus.PAID, 'bi-check', 'info'),
    (Order.OrderStatus.SHIPPED, 'bi-truck', 'primary'),
    (Order.OrderStatus.DELIVERED, 'bi-bag-check', 'success'),
)


def build_order_timeline(order):
    if order.status == Order.OrderStatus.CANCELLED:
        return None

    statuses = [status for status, _, _ in ORDER_TIMELINE_STEPS]
    current_index = statuses.index(order.status)
    status_labels = dict(Order.OrderStatus.choices)

    history_by_status = {}
    for entry in order.order_status_history.order_by('changed_at'):
        history_by_status[entry.new_status] = entry.changed_at

    steps = []
    for index, (status, icon, color) in enumerate(ORDER_TIMELINE_STEPS):
        reached = index <= current_index
        is_current = index == current_index
        timestamp = order.created_at if status == Order.OrderStatus.PAID else history_by_status.get(status)
        steps.append({
            'label': status_labels[status],
            'icon': icon,
            'color': color,
            'reached': reached,
            'current': is_current,
            'timestamp': timestamp if reached else None,
        })
    return steps

def fulfill_cart_checkout(session):

    if session.payment_status != 'paid':
        return None, False
    existing = Order.objects.filter(stripe_payment_id=session.id).first()
    if existing:
        return existing, False
    metadata = getattr(session, 'metadata', None) or {}
    if 'kind' not in metadata or metadata['kind'] != 'cart_order':
        return None, False

    user_id = metadata['user_id'] if 'user_id' in metadata else None
    address_id = metadata['address_id'] if 'address_id' in metadata else None
    items_json = metadata['items'] if 'items' in metadata else None
    if not user_id or not address_id or not items_json:
        logger.warning('Stripe session %s: missing cart order metadata', session.id)
        return None, False

    try:
        user_id = int(user_id)
        address_id = int(address_id)
        item_pairs = [(int(pid), int(qty)) for pid, qty in json.loads(items_json)]
        address = Address.objects.get(id=address_id, user_id=user_id)
    except (Address.DoesNotExist, ValueError, TypeError):
        logger.warning('Stripe session %s: invalid cart order metadata', session.id)
        return None, False

    with transaction.atomic():
        product_ids = sorted({pid for pid, _ in item_pairs})
        # during this transfer the concrete products are locked using select_for_update
        locked_products = {
            p.id: p for p in Product.objects.select_for_update().filter(id__in=product_ids)
        }
        for product_id, quantity in item_pairs:
            product = locked_products.get(product_id)
            if product is None or product.stock_quantity < quantity:
                logger.error(
                    'Stripe session %s paid but product %s is no longer available; refunding',
                    session.id, product_id,
                )
                try:
                    stripe.Refund.create(payment_intent=session.payment_intent)
                except Exception:
                    logger.exception('Stripe session %s: automatic refund failed', session.id)
                notify_staff(
                    type=Notification.Type.NEW_ORDER,
                    message=f'Плащане (сесия {session.id}) не можа да се обработи поради изчерпана наличност - сумата е възстановена.',
                )
                return None, False

        order = Order.objects.create(user_id=user_id, address=address, total_price=0,
            stripe_payment_id=session.id, status=Order.OrderStatus.PAID,
        )
        total_price = 0
        for product_id, quantity in item_pairs:
            product = locked_products[product_id]
            order_item = OrderItem.objects.create(
                order=order, product=product, quantity=quantity, price_at_purchase=product.price,
            )
            total_price += order_item.get_subtotal()
            product.stock_quantity -= quantity
            product.save(update_fields=['stock_quantity'])

        order.total_price = total_price
        order.save(update_fields=['total_price'])

        cart = Cart.objects.filter(user_id=user_id).first()
        if cart:
            cart.item.filter(product_id__in=product_ids).delete()

    return order, True
