from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('operator', 'Operator'),
        ('kasubag_umum', 'Kasubag Umum'),
    ]
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('nonaktif', 'Nonaktif'),
    ]
    UNIT_KERJA_CHOICES = [
        ('Sekretariat', 'Sekretariat'),
        ('Bagian Perencanaan Program & Keuangan DPPKB', 'Bagian Perencanaan Program & Keuangan DPPKB'),
        ('Bagian Umum dan Kepegawaian DPPKB', 'Bagian Umum dan Kepegawaian DPPKB'),
        ('Bidang DaldukP2 DPPKB', 'Bidang DaldukP2 DPPKB'),
        ('Bidang KB DPPKB', 'Bidang KB DPPKB'),
        ('Bidang K3 DPPKB', 'Bidang K3 DPPKB'),
        ('Balai Loa Janan Ilir', 'Balai Loa Janan Ilir'),
        ('Balai Palaran', 'Balai Palaran'),
        ('Balai Samarinda Ilir', 'Balai Samarinda Ilir'),
        ('Balai Samarinda Kota', 'Balai Samarinda Kota'),
        ('Balai Samarinda Seberang', 'Balai Samarinda Seberang'),
        ('Balai Samarinda Ulu', 'Balai Samarinda Ulu'),
        ('Balai Samarinda Utara', 'Balai Samarinda Utara'),
        ('Balai Sambutan', 'Balai Sambutan'),
        ('Balai Sungai Kunjang', 'Balai Sungai Kunjang'),
        ('Balai Sungai Pinang', 'Balai Sungai Pinang'),
    ]
    JENIS_AKUN_CHOICES = [
        ('umum', 'Umum'),
        ('balai', 'Balai'),
        ('bidang', 'Bidang'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nama_lengkap = models.CharField(max_length=150)
    jabatan = models.CharField(max_length=150, blank=True)
    unit_kerja = models.CharField(max_length=100, choices=UNIT_KERJA_CHOICES, blank=True)
    jenis_akun = models.CharField(max_length=10, choices=JENIS_AKUN_CHOICES, default='umum')
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
        'kasubag_umum': ['Dashboard', 'Manajemen Aset', 'Approval Service/Pemeliharaan'],
    }

    @property
    def hak_akses(self):
        return self.HAK_AKSES_MAP.get(self.role, [])