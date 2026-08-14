from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ActivityLog
from databarang.models import BarangATK, StokUnit


@login_required
def dashboard(request):
    profile = getattr(request.user, 'profile', None)

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

    aktivitas_list = ActivityLog.objects.all()[:5]
    return render(request, 'dashboard.html', {'aktivitas_list': aktivitas_list})