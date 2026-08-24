from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from .models import ActivityLog
from databarang.models import BarangATK, StokUnit, PermintaanDinas
from asset.models import Asset, PermintaanService
from pengguna.models import Profile


def is_kasubag_umum(user):
    return hasattr(user, 'profile') and user.profile.role == 'kasubag_umum'


@login_required
def dashboard(request):
    profile = getattr(request.user, 'profile', None)

    if is_kasubag_umum(request.user):
        unit_choices = Profile.UNIT_KERJA_CHOICES
        unit_filter = request.GET.get('unit', unit_choices[0][0] if unit_choices else '')

        query = request.GET.get('q', '')
        kategori = request.GET.get('kategori', '')

        daftar_barang = BarangATK.objects.all()
        if kategori:
            daftar_barang = daftar_barang.filter(kategori=kategori)
        if query:
            daftar_barang = daftar_barang.filter(
                Q(kode_barang__icontains=query) | Q(nama_barang__icontains=query)
            )

        top_barang = BarangATK.objects.all().order_by('-stok')[:5]

        permintaan_atk = PermintaanDinas.objects.all()
        permintaan_service = PermintaanService.objects.all()

        stok_unit_terpilih = StokUnit.objects.filter(unit_kerja=unit_filter) if unit_filter else []

        context = {
            'daftar_barang': daftar_barang,
            'top_barang': top_barang,
            'query': query,
            'kategori_aktif': kategori,

            'total_atk_pending': permintaan_atk.filter(status='diajukan').count(),
            'total_service_pending': permintaan_service.filter(status='diajukan').count(),
            'total_asset': Asset.objects.count(),
            'total_stok_menipis': BarangATK.objects.filter(stok__gt=0, stok__lt=10).count(),
            'total_stok_habis': BarangATK.objects.filter(stok=0).count(),

            'atk_diajukan': permintaan_atk.filter(status='diajukan').count(),
            'atk_disetujui': permintaan_atk.filter(status='disetujui').count(),
            'atk_ditolak': permintaan_atk.filter(status='ditolak').count(),

            'service_diajukan': permintaan_service.filter(status='diajukan').count(),
            'service_disetujui': permintaan_service.filter(status='disetujui').count(),
            'service_ditolak': permintaan_service.filter(status='ditolak').count(),

            'permintaan_atk_list': permintaan_atk.order_by('-diajukan_pada')[:10],
            'permintaan_service_list': permintaan_service.order_by('-diajukan_pada')[:10],

            'unit_filter': unit_filter,
            'stok_unit_terpilih': stok_unit_terpilih,
        }
        return render(request, 'dashboard_kasubag.html', context)

    if profile and profile.jenis_akun in ['balai', 'bidang']:
        stok_unit = StokUnit.objects.filter(unit_kerja=profile.unit_kerja)
        stok_pusat = BarangATK.objects.all()

        total_stok_unit = stok_unit.count()
        stok_unit_menipis = stok_unit.filter(stok__gt=0, stok__lt=10)
        stok_unit_habis = stok_unit.filter(stok=0)

        perlu_restock = (stok_unit_menipis | stok_unit_habis).order_by('stok')[:8]

        total_aman = total_stok_unit - stok_unit_menipis.count() - stok_unit_habis.count()

        context = {
            'unit_kerja': profile.unit_kerja,
            'total_stok_unit': total_stok_unit,
            'stok_unit_menipis': stok_unit_menipis.count(),
            'stok_unit_habis': stok_unit_habis.count(),
            'daftar_stok_unit': stok_unit[:5],
            'daftar_stok_pusat': stok_pusat[:8],

            'perlu_restock': perlu_restock,
            'total_aman': total_aman,
        }
        return render(request, 'dashboard_unit.html', context)

    aktivitas_list = ActivityLog.objects.all()[:5]
    return render(request, 'dashboard.html', {'aktivitas_list': aktivitas_list})