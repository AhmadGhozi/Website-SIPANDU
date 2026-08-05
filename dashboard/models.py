from django.db import models
from django.contrib.auth.models import User


class ActivityLog(models.Model):
    AKSI_CHOICES = [
        ('created', 'Ditambahkan'),
        ('updated', 'Diperbarui'),
        ('deleted', 'Dihapus'),
    ]

    aksi = models.CharField(max_length=10, choices=AKSI_CHOICES)
    deskripsi = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    dibuat_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-dibuat_pada']

    def __str__(self):
        return f"{self.get_aksi_display()} - {self.deskripsi}"

    @property
    def badge_class(self):
        return {
            'created': 'bg-success-subtle text-success',
            'updated': 'bg-primary-subtle text-primary',
            'deleted': 'bg-danger-subtle text-danger',
        }.get(self.aksi, 'bg-secondary-subtle text-secondary')