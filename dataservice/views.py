from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncMonth
from asset.models import RiwayatService


def is_umum_or_kasubag(user):
    profile = getattr(user, 'profile', None)
    if not profile:
        return False
    return profile.jenis_akun == 'umum' or profile.role == 'kasubag_umum'

@login_required
def data_service_list(request):
    if not is_umum_or_kasubag(request.user):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('dashboard')
    
    query = request.GET.get('q', '')
    jenis_filter = request.GET.get('jenis', '')

    riwayat = RiwayatService.objects.select_related('asset').all()

    if jenis_filter:
        riwayat = riwayat.filter(jenis_service=jenis_filter)

    if query:
        riwayat = riwayat.filter(
            Q(asset__nama_barang__icontains=query) |
            Q(asset__kode_barang__icontains=query) |
            Q(jenis_service__icontains=query)
        )

    semua_riwayat = RiwayatService.objects.all()

    total_service = semua_riwayat.count()
    total_biaya = semua_riwayat.aggregate(total=Sum('biaya'))['total'] or 0
    jenis_unik = semua_riwayat.values('jenis_service').distinct().count()

    ringkasan_per_asset = (
        semua_riwayat
        .values('asset__id', 'asset__nama_barang', 'asset__kode_barang')
        .annotate(total_service=Count('id'), total_biaya=Sum('biaya'))
        .order_by('-total_biaya')[:6]
    )
    max_biaya_asset = max([r['total_biaya'] or 0 for r in ringkasan_per_asset], default=1)

    tren_bulanan = (
        semua_riwayat
        .annotate(bulan=TruncMonth('tanggal'))
        .values('bulan')
        .annotate(total=Sum('biaya'))
        .order_by('bulan')
    )

    distribusi_jenis = (
        semua_riwayat
        .values('jenis_service')
        .annotate(total=Count('id'))
        .order_by('-total')[:8]
    )

    daftar_jenis = semua_riwayat.values_list('jenis_service', flat=True).distinct()

    context = {
        'riwayat': riwayat,
        'query': query,
        'jenis_filter': jenis_filter,
        'daftar_jenis': daftar_jenis,
        'total_service': total_service,
        'total_biaya': total_biaya,
        'jenis_unik': jenis_unik,
        'ringkasan_per_asset': ringkasan_per_asset,
        'max_biaya_asset': max_biaya_asset,
        'tren_bulanan': tren_bulanan,
        'distribusi_jenis': distribusi_jenis,
    }
    return render(request, 'dataservice/data_service_list.html', context)