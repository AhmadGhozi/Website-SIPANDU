from django.db import models
from django.contrib.auth.models import User


class SuratMasuk(models.Model):
    SIFAT_CHOICES = [
        ('biasa', 'Biasa'),
        ('penting', 'Penting'),
        ('segera', 'Segera'),
        ('rahasia', 'Rahasia'),
    ]

    nomor_agenda = models.CharField(max_length=30, verbose_name="Nomor Agenda")
    nomor_surat = models.CharField(max_length=100, verbose_name="Nomor Surat")
    asal_surat = models.CharField(max_length=150, verbose_name="Asal Surat")
    perihal = models.CharField(max_length=255, verbose_name="Perihal")
    sifat = models.CharField(max_length=10, choices=SIFAT_CHOICES, default='biasa')

    tanggal_surat = models.DateField(verbose_name="Tanggal Surat")
    tanggal_diterima = models.DateField(verbose_name="Tanggal Diterima")

    file_scan = models.FileField(upload_to='surat_masuk/%Y/%m/', verbose_name="File Scan Surat")

    dicatat_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='surat_masuk_dicatat')
    dicatat_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-tanggal_diterima', '-dicatat_pada']
        verbose_name = "Surat Masuk"
        verbose_name_plural = "Surat Masuk"

    def __str__(self):
        return f"{self.nomor_surat} - {self.perihal}"

    @property
    def badge_sifat(self):
        return {
            'biasa': 'bg-secondary-subtle text-secondary',
            'penting': 'bg-warning-subtle text-warning',
            'segera': 'bg-danger-subtle text-danger',
            'rahasia': 'bg-dark-subtle text-dark',
        }.get(self.sifat, 'bg-secondary-subtle text-secondary')


class SuratKeluar(models.Model):
    SIFAT_CHOICES = [
        ('biasa', 'Biasa'),
        ('penting', 'Penting'),
        ('segera', 'Segera'),
        ('rahasia', 'Rahasia'),
    ]

    nomor_agenda = models.CharField(max_length=30, verbose_name="Nomor Agenda")
    nomor_surat = models.CharField(max_length=100, verbose_name="Nomor Surat")
    tujuan_surat = models.CharField(max_length=150, verbose_name="Tujuan Surat")
    perihal = models.CharField(max_length=255, verbose_name="Perihal")
    sifat = models.CharField(max_length=10, choices=SIFAT_CHOICES, default='biasa')

    tanggal_surat = models.DateField(verbose_name="Tanggal Surat")

    file_scan = models.FileField(upload_to='surat_keluar/%Y/%m/', verbose_name="File Surat")

    dibuat_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='surat_keluar_dibuat')
    dibuat_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-tanggal_surat', '-dibuat_pada']
        verbose_name = "Surat Keluar"
        verbose_name_plural = "Surat Keluar"

    def __str__(self):
        return f"{self.nomor_surat} - {self.perihal}"

    @property
    def badge_sifat(self):
        return {
            'biasa': 'bg-secondary-subtle text-secondary',
            'penting': 'bg-warning-subtle text-warning',
            'segera': 'bg-danger-subtle text-danger',
            'rahasia': 'bg-dark-subtle text-dark',
        }.get(self.sifat, 'bg-secondary-subtle text-secondary')