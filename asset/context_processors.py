from .models import Asset


def notifikasi_asset(request):
    if not request.user.is_authenticated:
        return {}

    profile = getattr(request.user, 'profile', None)
    if not profile:
        return {}

    if profile.jenis_akun in ['balai', 'bidang']:
        daftar_asset = Asset.objects.filter(lokasi=profile.unit_kerja, kategori='kendaraan')
    else:
        daftar_asset = Asset.objects.filter(kategori='kendaraan')

    jumlah_bermasalah = 0
    for asset in daftar_asset:
        if asset.status_pajak['status'] in ['mendekati', 'terlambat']:
            jumlah_bermasalah += 1
        if asset.status_ganti_oli['status'] in ['mendekati', 'terlambat']:
            jumlah_bermasalah += 1

    return {'jumlah_asset_bermasalah': jumlah_bermasalah}