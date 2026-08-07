from django.urls import path
from . import views

app_name = 'databarang'

urlpatterns = [
    path('', views.barang_list, name='barang_list'),
    path('tambah/', views.barang_create, name='barang_create'),
    path('<int:pk>/edit/', views.barang_update, name='barang_update'),
    path('<int:pk>/hapus/', views.barang_delete, name='barang_delete'),
]