from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render

from admin_panel.models import User
from core.rate_limit import check_rate_limit, clear_rate_limit, get_client_ip

_ADMIN_LOGIN_MAX = 5
_ADMIN_LOGIN_WINDOW = 300  # 5 minutes


def login(request):
    if request.user.is_authenticated:
        return redirect('admin:dashboard')
    if request.method == 'POST':
        ip = get_client_ip(request)
        rate_key = f'admin_login:{ip}'
        if check_rate_limit(rate_key, max_attempts=_ADMIN_LOGIN_MAX, window_seconds=_ADMIN_LOGIN_WINDOW):
            messages.error(request, 'Too many login attempts. Please wait a few minutes before trying again.')
            return render(request, 'admin/login.html')

        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            clear_rate_limit(rate_key)
            request.session.cycle_key()  # Prevent session fixation
            django_login(request, user)
            return redirect('admin:dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'admin/login.html')


def logout(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    django_logout(request)
    return redirect('admin:login')
