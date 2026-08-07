from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('operator', 'Operator'),
    ]
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('nonaktif', 'Nonaktif'),
    ]
    UNIT_KERJA_CHOICES = [
        ('Sekretariat', 'Sekretariat'),
        ('Sub Bagian Perencanaan Program & Keuangan', 'Sub Bagian Perencanaan Program & Keuangan'),
        ('Sub Bagian Umum dan Kepegawaian', 'Sub Bagian Umum dan Kepegawaian'),
        ('Bidang Pengendalian Penduduk, Penyuluhan dan Penggerakan', 'Bidang Pengendalian Penduduk, Penyuluhan dan Penggerakan'),
        ('Bidang Keluarga Berencana', 'Bidang Keluarga Berencana'),
        ('Bidang Ketahanan dan Kesejahteraan Keluarga', 'Bidang Ketahanan dan Kesejahteraan Keluarga'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nama_lengkap = models.CharField(max_length=150)
    jabatan = models.CharField(max_length=150, blank=True)
    unit_kerja = models.CharField(max_length=100, choices=UNIT_KERJA_CHOICES, blank=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='operator')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='aktif')

    dibuat_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Pengguna'
        verbose_name_plural = 'Pengguna'

    def __str__(self):
        return self.nama_lengkap

    @property
    def id_pengguna(self):
        return f"USR-{self.pk:03d}"

    @property
    def inisial(self):
        return self.nama_lengkap[:1].upper() if self.nama_lengkap else "?"

    HAK_AKSES_MAP = {
        'admin': ['Dashboard', 'Manajemen Aset', 'Persuratan', 'Permintaan ATK', 'Pengaturan', 'Laporan'],
        'manager': ['Dashboard', 'Manajemen Aset', 'Persuratan', 'Permintaan ATK', 'Laporan'],
        'operator': ['Dashboard', 'Manajemen Aset', 'Persuratan', 'Permintaan ATK'],
    }

    @property
    def hak_akses(self):
        return self.HAK_AKSES_MAP.get(self.role, [])