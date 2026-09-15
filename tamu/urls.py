from django.urls import path
from . import views

app_name = 'tamu'

urlpatterns = [
    path('', views.permintaan_data_list, name='permintaan_data_list'),
    path('ajukan/', views.permintaan_data_create, name='permintaan_data_create'),
    path('<int:pk>/', views.permintaan_data_detail, name='permintaan_data_detail'),
]