from django.urls import path
from . import views

app_name = 'pengguna'

urlpatterns = [
    path('', views.pengguna_list, name='pengguna_list'),
    path('tambah/', views.pengguna_create, name='pengguna_create'),
    path('<int:pk>/', views.pengguna_detail, name='pengguna_detail'),
    path('<int:pk>/edit/', views.pengguna_update, name='pengguna_update'),
    path('<int:pk>/hapus/', views.pengguna_delete, name='pengguna_delete'),
]