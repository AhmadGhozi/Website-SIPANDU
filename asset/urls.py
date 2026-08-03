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
]