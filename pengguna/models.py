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

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nama_lengkap = models.CharField(max_length=150)
    jabatan = models.CharField(max_length=150, blank=True)
    unit_kerja = models.CharField(max_length=150, blank=True)
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