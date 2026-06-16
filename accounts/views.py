from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView, LogoutView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy

from .forms import RegistrationForm, LoginForm
# Create your views here.
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            first_name = form.cleaned_data.get('first_name')
            messages.success(request, f"{first_name}, регистрацията е успешна. Влезте в профила си.")
            return redirect('accounts:login')
    else:
        form = RegistrationForm()
        #print(form.errors)

    return render(request, "accounts/registration.html",{'form':form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
        # return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('accounts:profile')
                # return redirect('home')
            else:
                messages.error(request, "Грешен имейл или парола.")
        else:
            messages.error(request, "Невалиден формат на данни. Моля, опитайте отново.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form':form})

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')

class CustomLogoutView(LogoutView):
    next_page = 'accounts:login' # home
