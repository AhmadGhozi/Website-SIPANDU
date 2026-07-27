from django.contrib import admin
from django.urls import path, include
from dashboard.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', dashboard, name='dashboard'),
]