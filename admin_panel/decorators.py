from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def permission_required(permission):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('admin:login')
            checker = getattr(user, 'has_permission', None)
            if callable(checker) and checker(permission):
                return view_func(request, *args, **kwargs)
            messages.error(request, 'Your role does not have access to that area.')
            return redirect('admin:dashboard')

        return wrapped

    return decorator
