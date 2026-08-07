from django.db import models

class BarangATK(models.Model):
    SATUAN_CHOICES = [
        ('pcs', 'Pcs'),
        ('rim', 'Rim'),
        ('box', 'Box'),
        ('botol', 'Botol'),
        ('lusin', 'Lusin'),
        ('pak', 'Pak'),
        ('unit', 'Unit'),
    ]

    kode_barang = models.CharField(max_length=30, unique=True, verbose_name="Kode Barang")
    nama_barang = models.CharField(max_length=150, verbose_name="Nama Barang")
    satuan = models.CharField(max_length=10, choices=SATUAN_CHOICES, default='pcs')
    stok = models.PositiveIntegerField(default=0, verbose_name="Stok Tersedia")
    keterangan = models.TextField(blank=True, null=True)

    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diperbarui_pada = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nama_barang']
        verbose_name = "Barang ATK"
        verbose_name_plural = "Barang ATK"

    def __str__(self):
        return f"{self.nama_barang} ({self.stok} {self.get_satuan_display()})"

    @property
    def status_stok(self):
        if self.stok == 0:
            return 'habis'
        elif self.stok <= 5:
            return 'menipis'
        return 'aman'