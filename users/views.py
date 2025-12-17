from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from materials.models import Payment
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings

def home(request):
    return render(request, 'users/home.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}! You can now login.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                # Respect 'next' parameter when present (safe redirect).
                # Accept relative URLs (start with '/') or validate full URLs.
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url:
                    is_relative = str(next_url).startswith('/')
                    is_safe = url_has_allowed_host_and_scheme(next_url, allowed_hosts=set(settings.ALLOWED_HOSTS) or {request.get_host()})
                    if is_relative or is_safe:
                        return redirect(next_url)
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def payment_history(request):
    """Display user's payment history"""
    payments = Payment.objects.filter(
        user=request.user
    ).select_related('category').order_by('-created_at')
    
    context = {
        'payments': payments
    }
    return render(request, 'users/payment_history.html', context)

@login_required
def profile(request):
    """Display user profile"""
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'users/profile.html', context)
