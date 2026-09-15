from django.contrib import admin
from .models import PermintaanData


@admin.register(PermintaanData)
class PermintaanDataAdmin(admin.ModelAdmin):
    list_display = ['pemohon', 'asal_instansi', 'keperluan', 'status', 'diajukan_pada']
    list_filter = ['status']
    search_fields = ['asal_instansi', 'keperluan', 'data_diminta']