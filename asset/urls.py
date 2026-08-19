from django.urls import path
from . import views

app_name = 'asset'

urlpatterns = [
    path('', views.asset_list, name='asset_list'),
    path('tambah/', views.asset_create, name='asset_create'),
    path('<int:pk>/', views.asset_detail, name='asset_detail'),
    path('<int:pk>/edit/', views.asset_update, name='asset_update'),
    path('<int:pk>/hapus/', views.asset_delete, name='asset_delete'),
    path('<int:pk>/qrcode/', views.asset_qrcode, name='asset_qrcode'),
    path('qrcode-massal/', views.asset_qrcode_massal, name='asset_qrcode_massal'),
    path('<int:pk>/publik/', views.asset_public_detail, name='asset_public_detail'),
    path('<int:pk>/service/', views.asset_service_list, name='asset_service_list'),
    path('permintaan-service/ajukan/', views.permintaan_service_create, name='permintaan_service_create'),
    path('permintaan-service/', views.permintaan_service_list, name='permintaan_service_list'),
    path('permintaan-service/<int:pk>/', views.permintaan_service_detail, name='permintaan_service_detail'),
    path('permintaan-service/<int:pk>/edit/', views.permintaan_service_update, name='permintaan_service_update'),
    path('permintaan-service/<int:pk>/hapus/', views.permintaan_service_delete, name='permintaan_service_delete'),
]