from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ActivityLog
from databarang.models import BarangATK, StokUnit, PermintaanDinas
from asset.models import Asset, PermintaanService
from pengguna.models import Profile


def is_kasubag_umum(user):
    return hasattr(user, 'profile') and user.profile.role == 'kasubag_umum'


@login_required
def dashboard(request):
    profile = getattr(request.user, 'profile', None)

    # Dashboard khusus Kasubag Umum
    if is_kasubag_umum(request.user):
        unit_filter = request.GET.get('unit', '')

        stok_dinas = BarangATK.objects.all()

        stok_unit_terpilih = None
        if unit_filter:
            stok_unit_terpilih = StokUnit.objects.filter(unit_kerja=unit_filter)

        context = {
            'stok_dinas': stok_dinas,
            'unit_filter': unit_filter,
            'stok_unit_terpilih': stok_unit_terpilih,
            'total_atk_pending': PermintaanDinas.objects.filter(status='diajukan').count(),
            'total_service_pending': PermintaanService.objects.filter(status='diajukan').count(),
            'total_asset': Asset.objects.count(),
            'total_stok_menipis': stok_dinas.filter(stok__gt=0, stok__lte=5).count(),
            'total_stok_habis': stok_dinas.filter(stok=0).count(),
        }
        return render(request, 'dashboard_kasubag.html', context)

    # Dashboard khusus Balai/Bidang
    if profile and profile.jenis_akun in ['balai', 'bidang']:
        stok_unit = StokUnit.objects.filter(unit_kerja=profile.unit_kerja)
        stok_pusat = BarangATK.objects.all()

        context = {
            'unit_kerja': profile.unit_kerja,
            'total_stok_unit': stok_unit.count(),
            'stok_unit_menipis': stok_unit.filter(stok__gt=0, stok__lte=5).count(),
            'stok_unit_habis': stok_unit.filter(stok=0).count(),
            'daftar_stok_unit': stok_unit[:5],
            'daftar_stok_pusat': stok_pusat[:8],
        }
        return render(request, 'dashboard_unit.html', context)

    # Dashboard default (Admin/Umum)
    aktivitas_list = ActivityLog.objects.all()[:5]
    return render(request, 'dashboard.html', {'aktivitas_list': aktivitas_list})