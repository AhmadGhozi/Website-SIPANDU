from .models import Disposisi


def notifikasi_disposisi(request):
    if not request.user.is_authenticated:
        return {}

    profile = getattr(request.user, 'profile', None)
    if not profile or profile.jenis_akun not in ['balai', 'bidang']:
        return {}

    jumlah = Disposisi.objects.filter(
        status='menunggu',
        unit_tujuan__contains=profile.unit_kerja,
    ).count()

    return {'jumlah_disposisi_menunggu': jumlah}