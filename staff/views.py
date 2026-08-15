from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from communication.models import ContactMessage
from orders.models import Order
from .models import Notification, NotificationRecipient


# Create your views here.
@staff_member_required
def staff_dashboard_view(request):
    contact_messages = ContactMessage.objects.filter(is_resolved=False).count()
    orders = Order.objects.filter(status=Order.OrderStatus.PENDING).count()
    last_messages = ContactMessage.objects.exclude(is_resolved=True).select_related('user').order_by('-created_at')[:4]
    last_orders = Order.objects.exclude(status=Order.OrderStatus.DELIVERED).select_related('user','address').order_by('-created_at')[:4]
    recent_notifications = NotificationRecipient.objects.filter(
        recipient=request.user
    ).select_related('notification').order_by('-notification__created_at')[:4]

    context = {
        'contact_messages': contact_messages,
        'orders': orders,
        'last_orders': last_orders,
        'last_messages':last_messages,
        'recent_notifications': recent_notifications,
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

