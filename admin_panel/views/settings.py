from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


@login_required
def placeholder(request):
    return HttpResponse('Admin settings views scaffolded.')
