from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ActivityLog


@login_required
def dashboard(request):
    aktivitas_list = ActivityLog.objects.all()[:5]
    return render(request, 'dashboard.html', {'aktivitas_list': aktivitas_list})