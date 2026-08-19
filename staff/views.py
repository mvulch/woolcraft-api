from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from communication.models import ContactMessage
from orders.models import Order
from products.models import ProductReview
from .models import Notification, NotificationRecipient


# Create your views here.
@staff_member_required
def staff_dashboard_view(request):
    contact_messages = ContactMessage.objects.filter(is_resolved=False).count()
    orders = Order.objects.filter(status=Order.OrderStatus.PENDING).count()
    last_messages = ContactMessage.objects.exclude(is_resolved=True).select_related('user').order_by('-created_at')[:4]
    last_orders = Order.objects.all().select_related('user','address').order_by('-created_at')[:4]
    recent_notifications = NotificationRecipient.objects.filter(
        recipient=request.user
    ).select_related('notification').order_by('-notification__created_at')[:4]
    pending_reviews = ProductReview.objects.filter(is_published=False).count()
    recent_reviews = ProductReview.objects.all().select_related('user','product').order_by('-created_at')[:4]
    context = {
        'contact_messages': contact_messages,
        'orders': orders,
        'last_orders': last_orders,
        'last_messages':last_messages,
        'recent_notifications': recent_notifications,
        'pending_reviews':pending_reviews,
        'recent_reviews':recent_reviews,
    }
    return render(request, 'staff/staff_dashboard.html', context)

@staff_member_required
def staff_contact_messages_list_view(request):
    staff_contact_messages = ContactMessage.objects.select_related('user').all()
    filter_resolvance = request.GET.get('filter', '')
    if filter_resolvance == 'unresolved':
        staff_contact_messages = staff_contact_messages.filter(is_resolved=False)
    elif filter_resolvance == 'resolved':
        staff_contact_messages = staff_contact_messages.filter(is_resolved=True)
    #elif filter_resolvance == 'all':
    #    contact_messages = contact_messages.all()

    paginator = Paginator(staff_contact_messages, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'current_filter': filter_resolvance,
        'is_staff_view': True,
    }
    return render(request,'communication/contact_messages.html', context)

@staff_member_required
def staff_orders_list_view(request):
    orders = Order.objects.select_related('user', 'address').order_by('-created_at')
    filter_status = request.GET.get('status','')
    if filter_status:
        orders = orders.filter(status=filter_status)
    paginator = Paginator(orders, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'status_choices': Order.OrderStatus.choices,
        'current_status': filter_status,
        'is_staff_view':True,
    }
    return render(request,'orders/order_list.html', context)

@staff_member_required
def staff_order_detail_view(request, order_id):
    order = get_object_or_404(Order.objects.select_related('user','address').prefetch_related('items__product'),
         id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.OrderStatus.choices):
            order.status = new_status
            order.save()
            messages.success(request, f'Статусът на поръчка #{order.id} е обновен на {order.get_status_display()}.')
        return redirect('staff:staff_order_detail', order_id=order.id)
    return render(request, 'orders/order_detail.html',{'order':order, 'is_staff_view': True})

@staff_member_required
def notifications_view(request):
    notification_recipient = NotificationRecipient.objects.filter(
        recipient=request.user).select_related('notification').order_by('-notification__created_at')

    filter_type = request.GET.get('type', '')
    if filter_type:
        notification_recipient = notification_recipient.filter(notification__type=filter_type)

    paginator = Paginator(notification_recipient, 2)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'page_obj':page_obj,
        'type_choices': Notification.Type.choices,
        'current_type':filter_type,
    }
    return render(request, 'staff/notifications.html', context)

@staff_member_required
def notification_is_read_view(request, notification_id):
    notification_recipient = get_object_or_404(NotificationRecipient, notification__id=notification_id, recipient=request.user)
    notification_recipient.is_read=True
    notification_recipient.save()
    if notification_recipient.notification.link:
        return redirect(notification_recipient.notification.link)
    return redirect('staff:staff_notifications')

@staff_member_required
def reviews_view(request):
    reviews_list = ProductReview.objects.select_related('user', 'product')
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'not_published':
        reviews_list = reviews_list.filter(is_published=False)
    elif filter_type == 'published':
        reviews_list = reviews_list.filter(is_published=True)
    paginator = Paginator(reviews_list, 2)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'page_obj':page_obj,
        'current_filter':filter_type,
    }
    return render(request, 'staff/staff_reviews_list.html', context)

@staff_member_required
def review_approve_view(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            review.is_published = True
            review.save()
            messages.success(request, f'Коментарът е одобрен.')
        elif action == 'disapprove':
            review.delete()
            messages.error(request, f'Коментарът е отхвърлен.')
            return redirect('staff:staff_reviews_list')
    return render(request, 'staff/staff_review_detail.html', {'review':review})

