from django.db import models


class Asset(models.Model):
    KONDISI_CHOICES = [
        ('baik', 'Baik'),
        ('kurang_baik', 'Kurang Baik'),
        ('rusak', 'Rusak'),
    ]

    kode_barang = models.CharField(max_length=30, unique=True, verbose_name="Kode Barang")
    nama_barang = models.CharField(max_length=150, verbose_name="Nama Barang")
    merk_type = models.CharField(max_length=150, verbose_name="Merk / Type")
    jumlah = models.PositiveIntegerField(default=0)
    harga_satuan = models.DecimalField(max_digits=15, decimal_places=2)
    kondisi = models.CharField(max_length=15, choices=KONDISI_CHOICES, default='baik')
    keterangan = models.TextField(blank=True, null=True, verbose_name="Keterangan")

    lokasi = models.CharField(max_length=150, blank=True, verbose_name="Lokasi")
    pengguna = models.CharField(max_length=150, blank=True, verbose_name="Pengguna/Pemegang Saat Ini")

    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diperbarui_pada = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['kode_barang']
        verbose_name = "Asset"
        verbose_name_plural = "Asset"

    def __str__(self):
        return f"{self.kode_barang} - {self.nama_barang}"

    @property
    def total_nilai(self):
        return self.jumlah * self.harga_satuan