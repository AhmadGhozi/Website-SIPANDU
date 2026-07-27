from django.db import models


class Asset(models.Model):
    kode_barang = models.CharField(max_length=20, unique=True, verbose_name="Kode Barang")
    nama_barang = models.CharField(max_length=150, verbose_name="Nama Barang")
    merk_type = models.CharField(max_length=150, verbose_name="Merk / Type")
    jumlah = models.PositiveIntegerField(default=0)
    harga_satuan = models.DecimalField(max_digits=15, decimal_places=2)

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