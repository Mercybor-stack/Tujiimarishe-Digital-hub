from django.shortcuts import render, redirect
import time
import logging
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from materials.models import Payment
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings

# Simple logging configuration for development so timing info appears in console
logging.basicConfig(level=logging.INFO)

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
        t0 = time.time()
        form = LoginForm(request, data=request.POST)
        t1 = time.time()
        if form.is_valid():
            t2 = time.time()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            t_auth_start = time.time()
            user = authenticate(username=username, password=password)
            t_auth_end = time.time()
            if user is not None:
                t_login_start = time.time()
                login(request, user)
                t_login_end = time.time()
                messages.success(request, f'Welcome back, {username}!')
                # Respect 'next' parameter when present (safe redirect).
                # Accept relative URLs (start with '/') or validate full URLs.
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url:
                    is_relative = str(next_url).startswith('/')
                    is_safe = url_has_allowed_host_and_scheme(next_url, allowed_hosts=set(settings.ALLOWED_HOSTS) or {request.get_host()})
                    if is_relative or is_safe:
                        # log timings before redirect
                        logging.getLogger(__name__).info(
                            f"login timings: form_init={(t1-t0):.3f}s, form_validate={(t2-t1):.3f}s, authenticate={(t_auth_end-t_auth_start):.3f}s, login={(t_login_end-t_login_start):.3f}s"
                        )
                        return redirect(next_url)
                # log timings
                logging.getLogger(__name__).info(
                    f"login timings: form_init={(t1-t0):.3f}s, form_validate={(t2-t1):.3f}s, authenticate={(t_auth_end-t_auth_start):.3f}s, login={(t_login_end-t_login_start):.3f}s"
                )
                return redirect('home')
            else:
                logging.getLogger(__name__).info(
                    f"login timings (failed): form_init={(t1-t0):.3f}s, form_validate={(t2-t1):.3f}s, authenticate={(t_auth_end-t_auth_start):.3f}s"
                )
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
