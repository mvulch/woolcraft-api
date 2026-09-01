from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from orders.models import Address
from .models import CustomRequest
from .forms import CustomRequestForm, CustomRequestMessageForm, OfferPriceForm
from staff.utils import notify_staff
from staff.models import Notification
import stripe
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def custom_request_create_view(request):
    if request.method == 'POST':
        form = CustomRequestForm(request.POST, request.FILES)
        if form.is_valid():
            custom_request = form.save(commit=False)
            custom_request.user = request.user
            custom_request.save()
            notify_staff(
                type=Notification.Type.NEW_REQUEST,
                message=f'Нова персонализирана заявка #{custom_request.id} от {custom_request.user.get_full_name()}',
                link=reverse('custom_requests:custom_request_detail', args=[custom_request.id]),
            )
            messages.success(request, 'Заявката Ви е изпратена успешно и очаква да бъде разгледана от нашия екип.')
            return redirect('custom_requests:custom_request_detail', request_id=custom_request.id)
    else:
        form = CustomRequestForm()
    return render(request, 'custom_requests/custom_request_create.html', {'form':form})

@login_required
def custom_requests_list_view(request):
    custom_requests = CustomRequest.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(custom_requests, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'custom_requests/custom_requests_list.html', context)

@login_required
def custom_request_detail_view(request, request_id):
    if request.user.is_staff:
        custom_request = get_object_or_404(CustomRequest.objects.select_related('user').prefetch_related('messages__user'),id=request_id)
    else:
        custom_request = get_object_or_404(CustomRequest.objects.select_related('user').prefetch_related('messages__user'),
                                          id=request_id, user=request.user)
    form = CustomRequestMessageForm()
    price_form = OfferPriceForm()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'message':
            form = CustomRequestMessageForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.user = request.user
                message.request = custom_request
                message.save()
                if request.user.is_staff:
                    # notification for user
                    pass
                else:
                    notify_staff(type=Notification.Type.NEW_REQUEST,
                                 message=f'Нов отговор на заявка #{custom_request.id}',
                                 link=reverse('custom_requests:custom_request_detail', args=[custom_request.id]), )
                messages.success(request, 'Съобщението е изпратено.')
                return redirect('custom_requests:custom_request_detail', request_id=custom_request.id)
        elif action == 'update_status' and request.user.is_staff:
            new_status = request.POST.get('status')
            if new_status in dict(CustomRequest.Status.choices):
                custom_request.status = new_status
                custom_request.save()
                messages.success(request, 'Статусът е обновен успешно.')
                return redirect('custom_requests:custom_request_detail', request_id=custom_request.id)
            else:
                messages.error(request, 'Невалиден статус.')

        elif action == 'offer_price' and request.user.is_staff:
            price_form = OfferPriceForm(request.POST)
            if price_form.is_valid():
                custom_request.offered_price = price_form.cleaned_data['offered_price']
                custom_request.status = CustomRequest.Status.PRICE_OFFERED
                custom_request.save(update_fields=['offered_price','status','updated_at'])
                # notify user for offered price
                messages.success(request, 'Цената е предложена.')
                return redirect('custom_requests:custom_request_detail', request_id=custom_request.id)

        elif action == 'client_decline' and not request.user.is_staff:
            if custom_request.status == CustomRequest.Status.PRICE_OFFERED:
                custom_request.status = CustomRequest.Status.DECLINED
                custom_request.save()
                notify_staff(
                    type=Notification.Type.NEW_REQUEST,
                    message=f'Отказана цена на персонализирана заявка #{custom_request.id} от клиент {custom_request.user.get_full_name()}',
                    link=reverse('custom_requests:custom_request_detail', args=[custom_request.id]),)
                messages.info(request, 'Отказахте предложената цена.')
                return redirect('custom_requests:custom_request_detail', request_id=custom_request.id)
    context = {
        'custom_request': custom_request,
        'form': form,
        'price_form': price_form,
    }
    return render(request, 'custom_requests/custom_request_detail.html', context)

@login_required
def custom_request_address_view(request, request_id):
    custom_request = get_object_or_404(CustomRequest, id=request_id, user=request.user, status=CustomRequest.Status.PRICE_OFFERED)

    addresses = Address.objects.filter(user=request.user)
    if not addresses.exists():
        messages.error(request, 'Добавете адрес за доставка')
        return redirect('orders:address_create')
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        address = get_object_or_404(Address, id=address_id, user=request.user)
        custom_request.address = address
        custom_request.save()
        return redirect('custom_requests:custom_request_payment', request_id=custom_request.id)

    context = {
        'custom_request': custom_request,
        'addresses': addresses,
        'default_address': addresses.filter(is_default=True).first(),
    }
    return render(request, 'custom_requests/address_select.html', context)


@login_required
def custom_request_payment_view(request, request_id):
    custom_request = get_object_or_404(CustomRequest, id=request_id, user=request.user, status=CustomRequest.Status.PRICE_OFFERED)
    if custom_request.offered_price is None:
        messages.error(request, 'Все още не е предложена цена за заявката.')
        return redirect('custom_request:custom_request_detail', request_id=custom_request.id)
    line_items = [{
        'price_data': {
            'currency': 'eur',
            'product_data': {'name': f'Персонализирана заявка - поръчка ръчна изработка #{custom_request.id} - {custom_request.title}.',},
            'unit_amount': int(custom_request.offered_price * 100),
        },
        'quantity': 1
    }]
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri(reverse('custom_requests:custom_request_payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(
            reverse('custom_requests:custom_request_detail', kwargs={'request_id': custom_request.id})
        ),
        metadata={'custom_request_id': custom_request.id},
    )
    custom_request.stripe_payment_id = session.id
    custom_request.save(update_fields=['stripe_id','updated_at'])
    return redirect(session.url, code=303)

@login_required
def custom_request_payment_success_view(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return redirect('home')
    session = stripe.checkout.Session.retrieve(session_id)
    custom_request_id = session.metadata['custom_request_id']
    custom_request = get_object_or_404(CustomRequest, id=custom_request_id, user=request.user)

    if session.payment_status == 'paid':
        custom_request.status = CustomRequest.Status.PAID
        custom_request.save()
        messages.success(request, f'Поръчката беше заплатена успешно. Очаквайте скоро да бъде изработена!')
        notify_staff(type=Notification.Type.NEW_REQUEST,
                     message=f'Персонализирана поръчка #{custom_request.id} беше заплатена от {request.user.get_full_name()}.',
                     link=f'/custom_requests/custom-request-detail/{custom_request.id}', )
    return redirect('custom_requests:custom_request_detail', request_id=custom_request.id)
