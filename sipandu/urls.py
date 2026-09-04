from django.contrib import admin
from django.urls import path, include
from dashboard.views import dashboard
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('asset/', include('asset.urls')),
    path('', dashboard, name='dashboard'),
    path('pengguna/', include('pengguna.urls')),
    path('databarang/', include('databarang.urls')),
    path('dataservice/', include('dataservice.urls')),
    path('persuratan/', include('persuratan.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)