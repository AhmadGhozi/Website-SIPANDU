from django.contrib import admin
from .models import SuratMasuk, SuratKeluar


@admin.register(SuratMasuk)
class SuratMasukAdmin(admin.ModelAdmin):
    list_display = ['nomor_surat', 'asal_surat', 'perihal', 'sifat', 'tanggal_diterima', 'dicatat_oleh']
    list_filter = ['sifat', 'tanggal_diterima']
    search_fields = ['nomor_surat', 'nomor_agenda', 'asal_surat', 'perihal']


@admin.register(SuratKeluar)
class SuratKeluarAdmin(admin.ModelAdmin):
    list_display = ['nomor_surat', 'tujuan_surat', 'perihal', 'sifat', 'tanggal_surat', 'dibuat_oleh']
    list_filter = ['sifat', 'tanggal_surat']
    search_fields = ['nomor_surat', 'nomor_agenda', 'tujuan_surat', 'perihal']