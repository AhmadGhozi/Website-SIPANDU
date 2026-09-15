from django.db import models
from django.contrib.auth.models import User


class PermintaanData(models.Model):
    STATUS_CHOICES = [
        ('diajukan', 'Diajukan'),
        ('diterima', 'Diterima'),
        ('ditolak', 'Ditolak'),
    ]

    pemohon = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permintaan_data')
    nama_pemohon = models.CharField(max_length=150, verbose_name="Nama Pemohon")
    asal_instansi = models.CharField(max_length=200, verbose_name="Asal Instansi/Kampus")
    keperluan = models.CharField(max_length=255, verbose_name="Keperluan")
    data_diminta = models.TextField(verbose_name="Data yang Diminta")

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='diajukan')
    catatan_tanggapan = models.TextField(blank=True, verbose_name="Catatan Tanggapan")

    diajukan_pada = models.DateTimeField(auto_now_add=True)
    diproses_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='permintaan_data_diproses')
    diproses_pada = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-diajukan_pada']
        verbose_name = "Permintaan Data"
        verbose_name_plural = "Permintaan Data"

    def __str__(self):
        return f"{self.pemohon.username} - {self.keperluan}"

    @property
    def badge_status(self):
        return {
            'diajukan': 'bg-secondary-subtle text-secondary',
            'diterima': 'bg-success-subtle text-success',
            'ditolak': 'bg-danger-subtle text-danger',
        }.get(self.status, 'bg-secondary-subtle text-secondary')