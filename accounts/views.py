from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import RegistrationForm, LoginForm
# Create your views here.
def register_view_test(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            print(f"is ok")
            form.save()
            messages.success(request, "Регистрацията е успешна. Влезте в профила си.")
            return redirect('accounts:login')
    else:

        form = RegistrationForm()
        print(form.errors)

    return render(request, "accounts/registration.html",{'form':form})

def login_view(request):
    # if request.user.is_authenticated:
    #    return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                print("OK")
                return redirect('accounts:login')
                # return redirect('home')
            else:
                messages.error(request, "Грешен имейл или парола.")
        else:
            messages.error(request, "Невалиден формат на данни. Моля, опитайте отново.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form':form})
