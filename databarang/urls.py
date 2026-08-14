from django.urls import path
from . import views

app_name = 'databarang'

urlpatterns = [
    path('', views.barang_list, name='barang_list'),
    path('tambah/', views.barang_create, name='barang_create'),
    path('<int:pk>/edit/', views.barang_update, name='barang_update'),
    path('<int:pk>/hapus/', views.barang_delete, name='barang_delete'),

    path('stok-unit/', views.stok_unit_list, name='stok_unit_list'),
    path('stok-unit/tambah/', views.stok_unit_create, name='stok_unit_create'),
    path('stok-unit/<int:pk>/edit/', views.stok_unit_update, name='stok_unit_update'),
    path('stok-unit/<int:pk>/hapus/', views.stok_unit_delete, name='stok_unit_delete'),

    path('permintaan-dinas/', views.permintaan_dinas_list, name='permintaan_dinas_list'),
    path('permintaan-dinas/ajukan/', views.permintaan_dinas_create, name='permintaan_dinas_create'),
    path('permintaan-dinas/<int:pk>/', views.permintaan_dinas_detail, name='permintaan_dinas_detail'),
]