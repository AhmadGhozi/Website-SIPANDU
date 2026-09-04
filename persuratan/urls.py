from django.urls import path
from . import views

app_name = 'persuratan'

urlpatterns = [
    path('surat-masuk/', views.surat_masuk_list, name='surat_masuk_list'),
    path('surat-masuk/tambah/', views.surat_masuk_create, name='surat_masuk_create'),
    path('surat-masuk/<int:pk>/', views.surat_masuk_detail, name='surat_masuk_detail'),
    path('surat-masuk/<int:pk>/edit/', views.surat_masuk_update, name='surat_masuk_update'),
    path('surat-masuk/<int:pk>/hapus/', views.surat_masuk_delete, name='surat_masuk_delete'),

    path('surat-keluar/', views.surat_keluar_list, name='surat_keluar_list'),
    path('surat-keluar/tambah/', views.surat_keluar_create, name='surat_keluar_create'),
    path('surat-keluar/<int:pk>/', views.surat_keluar_detail, name='surat_keluar_detail'),
    path('surat-keluar/<int:pk>/edit/', views.surat_keluar_update, name='surat_keluar_update'),
    path('surat-keluar/<int:pk>/hapus/', views.surat_keluar_delete, name='surat_keluar_delete'),
]