from django.db import models
from django.contrib.auth.models import User

class BarangATK(models.Model):
    KATEGORI_CHOICES = [
        ('atk', 'ATK'),
        ('bhp', 'BHP'),
    ]
    SATUAN_CHOICES = [
        ('pcs', 'Pcs'),
        ('rim', 'Rim'),
        ('box', 'Box'),
        ('botol', 'Botol'),
        ('lusin', 'Lusin'),
        ('pak', 'Pak'),
        ('unit', 'Unit'),
    ]

    kategori = models.CharField(max_length=5, choices=KATEGORI_CHOICES, default='atk')
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

class StokUnit(models.Model):
    SATUAN_CHOICES = [
        ('pcs', 'Pcs'),
        ('rim', 'Rim'),
        ('box', 'Box'),
        ('botol', 'Botol'),
        ('lusin', 'Lusin'),
        ('pak', 'Pak'),
        ('unit', 'Unit'),
    ]

    unit_kerja = models.CharField(max_length=100, verbose_name="Unit Kerja Pemilik")
    kode_barang = models.CharField(max_length=30, verbose_name="Kode Barang")
    nama_barang = models.CharField(max_length=150, verbose_name="Nama Barang")
    satuan = models.CharField(max_length=10, choices=SATUAN_CHOICES, default='pcs')
    stok = models.PositiveIntegerField(default=0, verbose_name="Stok Tersedia")
    keterangan = models.TextField(blank=True, null=True)

    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diperbarui_pada = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nama_barang']
        verbose_name = "Stok Barang Unit"
        verbose_name_plural = "Stok Barang Unit"
        unique_together = ['unit_kerja', 'kode_barang']

    def __str__(self):
        return f"{self.nama_barang} - {self.unit_kerja}"

    @property
    def status_stok(self):
        if self.stok == 0:
            return 'habis'
        elif self.stok <= 5:
            return 'menipis'
        return 'aman'

class PermintaanDinas(models.Model):
    STATUS_CHOICES = [
        ('diajukan', 'Diajukan'),
        ('disetujui', 'Disetujui'),
        ('ditolak', 'Ditolak'),
    ]

    unit_kerja = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='diajukan')
    catatan_approval = models.TextField(blank=True)

    diajukan_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='permintaan_dinas_diajukan')
    diajukan_pada = models.DateTimeField(auto_now_add=True)

    diproses_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='permintaan_dinas_diproses')
    diproses_pada = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-diajukan_pada']
        verbose_name = "Permintaan Ke Dinas"
        verbose_name_plural = "Permintaan Ke Dinas"

    def __str__(self):
        return f"Permintaan #{self.pk} - {self.unit_kerja}"

    @property
    def nomor(self):
        return f"PD-{self.pk:04d}"

    @property
    def badge_class(self):
        return {
            'diajukan': 'bg-warning-subtle text-warning',
            'disetujui': 'bg-success-subtle text-success',
            'ditolak': 'bg-danger-subtle text-danger',
        }.get(self.status, 'bg-secondary-subtle text-secondary')


class PermintaanDinasItem(models.Model):
    permintaan = models.ForeignKey(PermintaanDinas, on_delete=models.CASCADE, related_name='items')
    barang = models.ForeignKey(BarangATK, on_delete=models.CASCADE)
    jumlah = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.barang.nama_barang} x{self.jumlah}"