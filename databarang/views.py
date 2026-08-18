from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import BarangATK, StokUnit, PermintaanDinas, PermintaanDinasItem
from .forms import BarangATKForm, StokUnitForm
from dashboard.models import ActivityLog

def is_kasubag_umum(user):
    return hasattr(user, 'profile') and user.profile.role == 'kasubag_umum'

@login_required
def barang_list(request):
    query = request.GET.get('q', '')
    kategori = request.GET.get('kategori', '')
    daftar_barang = BarangATK.objects.all()

    if kategori:
        daftar_barang = daftar_barang.filter(kategori=kategori)

    if query:
        daftar_barang = daftar_barang.filter(
            Q(kode_barang__icontains=query) | Q(nama_barang__icontains=query)
        )

    context = {
        'daftar_barang': daftar_barang,
        'query': query,
        'kategori_aktif': kategori,
        'total_barang': BarangATK.objects.count(),
        'total_menipis': BarangATK.objects.filter(stok__gt=0, stok__lte=5).count(),
        'total_habis': BarangATK.objects.filter(stok=0).count(),
    }
    return render(request, 'databarang/barang_list.html', context)


@login_required
def barang_create(request):
    if request.method == 'POST':
        form = BarangATKForm(request.POST)
        if form.is_valid():
            barang = form.save()
            ActivityLog.objects.create(
                aksi='created',
                deskripsi=f"Barang ATK: {barang.nama_barang} ({barang.kode_barang})",
                user=request.user,
            )
            messages.success(request, 'Barang ATK baru berhasil ditambahkan.')
            return redirect('databarang:barang_list')
    else:
        form = BarangATKForm()

    context = {'form': form, 'judul': 'Tambah Barang ATK', 'subjudul': 'Lengkapi data barang baru', 'is_edit': False}
    return render(request, 'databarang/barang_form.html', context)


@login_required
def barang_update(request, pk):
    barang = get_object_or_404(BarangATK, pk=pk)
    if request.method == 'POST':
        form = BarangATKForm(request.POST, instance=barang)
        if form.is_valid():
            barang = form.save()
            ActivityLog.objects.create(
                aksi='updated',
                deskripsi=f"Barang ATK: {barang.nama_barang} ({barang.kode_barang})",
                user=request.user,
            )
            messages.success(request, 'Data barang berhasil diperbarui.')
            return redirect('databarang:barang_list')
    else:
        form = BarangATKForm(instance=barang)

    context = {'form': form, 'judul': 'Edit Barang ATK', 'subjudul': f'Kode: {barang.kode_barang}', 'is_edit': True}
    return render(request, 'databarang/barang_form.html', context)


@login_required
def barang_delete(request, pk):
    barang = get_object_or_404(BarangATK, pk=pk)
    if request.method == 'POST':
        ActivityLog.objects.create(
            aksi='deleted',
            deskripsi=f"Barang ATK: {barang.nama_barang} ({barang.kode_barang})",
            user=request.user,
        )
        barang.delete()
        messages.success(request, 'Barang ATK berhasil dihapus.')
    return redirect('databarang:barang_list')

def get_unit_kerja(request):
    """Helper: pastikan user adalah akun Balai/Bidang, kembalikan unit_kerja-nya."""
    profile = getattr(request.user, 'profile', None)
    if profile and profile.jenis_akun in ['balai', 'bidang']:
        return profile.unit_kerja
    return None


@login_required
def stok_unit_list(request):
    unit_kerja = get_unit_kerja(request)
    if not unit_kerja:
        messages.error(request, 'Halaman ini khusus untuk akun Balai/Bidang.')
        return redirect('dashboard')

    query = request.GET.get('q', '')
    daftar_stok = StokUnit.objects.filter(unit_kerja=unit_kerja)

    if query:
        daftar_stok = daftar_stok.filter(
            Q(kode_barang__icontains=query) | Q(nama_barang__icontains=query)
        )

    context = {
        'daftar_stok': daftar_stok,
        'query': query,
        'unit_kerja': unit_kerja,
        'total_barang': daftar_stok.count(),
        'total_menipis': daftar_stok.filter(stok__gt=0, stok__lte=5).count(),
        'total_habis': daftar_stok.filter(stok=0).count(),
    }
    return render(request, 'databarang/stok_unit_list.html', context)


@login_required
def stok_unit_create(request):
    unit_kerja = get_unit_kerja(request)
    if not unit_kerja:
        messages.error(request, 'Halaman ini khusus untuk akun Balai/Bidang.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = StokUnitForm(request.POST)
        if form.is_valid():
            stok = form.save(commit=False)
            stok.unit_kerja = unit_kerja
            stok.save()
            messages.success(request, 'Barang berhasil ditambahkan ke stok.')
            return redirect('databarang:stok_unit_list')
    else:
        form = StokUnitForm()

    context = {'form': form, 'judul': 'Tambah Stok Barang', 'subjudul': unit_kerja, 'is_edit': False}
    return render(request, 'databarang/stok_unit_form.html', context)


@login_required
def stok_unit_update(request, pk):
    unit_kerja = get_unit_kerja(request)
    if not unit_kerja:
        messages.error(request, 'Halaman ini khusus untuk akun Balai/Bidang.')
        return redirect('dashboard')

    stok = get_object_or_404(StokUnit, pk=pk, unit_kerja=unit_kerja)

    if request.method == 'POST':
        form = StokUnitForm(request.POST, instance=stok)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stok barang berhasil diperbarui.')
            return redirect('databarang:stok_unit_list')
    else:
        form = StokUnitForm(instance=stok)

    context = {'form': form, 'judul': 'Edit Stok Barang', 'subjudul': unit_kerja, 'is_edit': True}
    return render(request, 'databarang/stok_unit_form.html', context)


@login_required
def stok_unit_delete(request, pk):
    unit_kerja = get_unit_kerja(request)
    if not unit_kerja:
        messages.error(request, 'Halaman ini khusus untuk akun Balai/Bidang.')
        return redirect('dashboard')

    stok = get_object_or_404(StokUnit, pk=pk, unit_kerja=unit_kerja)
    if request.method == 'POST':
        stok.delete()
        messages.success(request, 'Stok barang berhasil dihapus.')
    return redirect('databarang:stok_unit_list')

@login_required
def permintaan_dinas_create(request):
    unit_kerja = get_unit_kerja(request)
    if not unit_kerja:
        messages.error(request, 'Halaman ini khusus untuk akun Balai/Bidang.')
        return redirect('dashboard')

    daftar_barang = BarangATK.objects.all()

    if request.method == 'POST':
        barang_ids = request.POST.getlist('barang_id')
        jumlahs = request.POST.getlist('jumlah')

        items_valid = []
        for barang_id, jumlah in zip(barang_ids, jumlahs):
            if barang_id and jumlah and int(jumlah) > 0:
                items_valid.append((barang_id, int(jumlah)))

        if not items_valid:
            messages.error(request, 'Tambahkan minimal 1 barang dengan jumlah yang valid.')
        else:
            permintaan = PermintaanDinas.objects.create(
                unit_kerja=unit_kerja,
                diajukan_oleh=request.user,
            )
            for barang_id, jumlah in items_valid:
                PermintaanDinasItem.objects.create(
                    permintaan=permintaan,
                    barang_id=barang_id,
                    jumlah=jumlah,
                )
            messages.success(request, 'Permintaan ke Dinas berhasil diajukan.')
            return redirect('databarang:permintaan_dinas_list')

    return render(request, 'databarang/permintaan_dinas_form.html', {
        'daftar_barang': daftar_barang, 'unit_kerja': unit_kerja,
    })


@login_required
def permintaan_dinas_list(request):
    permintaan_list = PermintaanDinas.objects.select_related('diajukan_oleh').prefetch_related('items__barang').all()

    unit_kerja = get_unit_kerja(request)
    if unit_kerja:
        permintaan_list = permintaan_list.filter(unit_kerja=unit_kerja)

    context = {
        'permintaan_list': permintaan_list,
        'is_approver': is_kasubag_umum(request.user),
        'is_balai_bidang': bool(unit_kerja),
        'total_diajukan': permintaan_list.filter(status='diajukan').count(),
        'total_disetujui': permintaan_list.filter(status='disetujui').count(),
        'total_ditolak': permintaan_list.filter(status='ditolak').count(),
    }
    return render(request, 'databarang/permintaan_dinas_list.html', context)


@login_required
def permintaan_dinas_detail(request, pk):
    permintaan = get_object_or_404(PermintaanDinas, pk=pk)
    is_approver = is_kasubag_umum(request.user)

    if request.method == 'POST':
        if not is_approver:
            messages.error(request, 'Anda tidak memiliki akses untuk memproses permintaan ini.')
            return redirect('databarang:permintaan_dinas_detail', pk=permintaan.pk)

        aksi = request.POST.get('aksi')
        catatan = request.POST.get('catatan_approval', '')

        if aksi == 'tolak':
            permintaan.status = 'ditolak'
            permintaan.catatan_approval = catatan
            permintaan.diproses_oleh = request.user
            permintaan.diproses_pada = timezone.now()
            permintaan.save()
            messages.success(request, 'Permintaan ditolak.')
            return redirect('databarang:permintaan_dinas_list')

        elif aksi == 'setuju':
            # Cek stok cukup untuk semua item sebelum diproses
            for item in permintaan.items.all():
                if item.jumlah > item.barang.stok:
                    messages.error(request, f'Stok "{item.barang.nama_barang}" tidak mencukupi (tersedia {item.barang.stok}, diminta {item.jumlah}).')
                    return redirect('databarang:permintaan_dinas_detail', pk=permintaan.pk)

            # Kurangi stok pusat
            for item in permintaan.items.all():
                item.barang.stok -= item.jumlah
                item.barang.save()

            permintaan.status = 'disetujui'
            permintaan.catatan_approval = catatan
            permintaan.diproses_oleh = request.user
            permintaan.diproses_pada = timezone.now()
            permintaan.save()
            messages.success(request, 'Permintaan disetujui, stok pusat telah diperbarui.')
            return redirect('databarang:permintaan_dinas_list')

    return render(request, 'databarang/permintaan_dinas_detail.html', {
        'permintaan': permintaan, 'is_approver': is_approver,
    })