from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import CustomRequest
from .forms import CustomRequestForm, CustomRequestMessageForm
from staff.utils import notify_staff
from staff.models import Notification
# Create your views here.
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
                link=f'/custom_requests/custom-request-detail/{custom_request.id}',
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
                                 link=f'/custom_requests/custom-request-detail/{custom_request.id}', )
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
    context = {
        'custom_request': custom_request,
        'form': form,
    }
    return render(request, 'custom_requests/custom_request_detail.html', context)