from django.urls import path
from . import views

app_name = 'dataservice'

urlpatterns = [
    path('', views.data_service_list, name='data_service_list'),
]