from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'حساب کاربری {username} با موفقیت ایجاد شد!')
            login(request, user)
            return redirect('product_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"شما با نام کاربری {username} وارد شدید.")
                return redirect('shop:product_list')
        else:
            messages.error(request, "نام کاربری یا رمز عبور نامعتبر است.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/signin.html', {'form': form})

def signout(request):
    logout(request)
    messages.info(request, "شما با موفقیت خارج شدید.")
    return redirect('shop:product_list')