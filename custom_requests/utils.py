from .models import CustomRequest

def mark_order_paid(custom_request_id):
    """Updates order status - price_offered -> paid; Returns True if updated"""
    updated = CustomRequest.objects.filter(id=custom_request_id, status=CustomRequest.Status.PRICE_OFFERED
                                           ).update(status=CustomRequest.Status.PAID)
    return bool(updated)