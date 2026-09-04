from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import SuratMasuk, SuratKeluar
from .forms import SuratMasukForm, SuratKeluarForm
from dashboard.models import ActivityLog


def is_umum_or_kasubag(user):
    profile = getattr(user, 'profile', None)
    if not profile:
        return False
    return profile.jenis_akun == 'umum' or profile.role == 'kasubag_umum'


# ===== SURAT MASUK =====

@login_required
def surat_masuk_list(request):
    if not is_umum_or_kasubag(request.user):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('dashboard')

    query = request.GET.get('q', '')
    daftar_surat = SuratMasuk.objects.all()

    if query:
        daftar_surat = daftar_surat.filter(
            Q(nomor_surat__icontains=query) |
            Q(asal_surat__icontains=query) |
            Q(perihal__icontains=query)
        )

    context = {
        'daftar_surat': daftar_surat,
        'query': query,
        'jumlah_surat': daftar_surat.count(),
    }
    return render(request, 'persuratan/surat_masuk_list.html', context)


@login_required
def surat_masuk_create(request):
    if not is_umum_or_kasubag(request.user):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = SuratMasukForm(request.POST, request.FILES)
        if form.is_valid():
            surat = form.save(commit=False)
            surat.dicatat_oleh = request.user
            surat.save()
            ActivityLog.objects.create(
                aksi='created',
                deskripsi=f"Surat Masuk: {surat.nomor_surat} - {surat.perihal}",
                user=request.user,
            )
            messages.success(request, 'Surat masuk berhasil dicatat.')
            return redirect('persuratan:surat_masuk_list')
    else:
        form = SuratMasukForm()

    context = {'form': form, 'judul': 'Tambah Surat Masuk', 'subjudul': 'Catat surat masuk baru', 'is_edit': False}
    return render(request, 'persuratan/surat_masuk_form.html', context)


@login_required
def surat_masuk_update(request, pk):
    if not is_umum_or_kasubag(request.user):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('dashboard')

    surat = get_object_or_404(SuratMasuk, pk=pk)

    if request.method == 'POST':
        form = SuratMasukForm(request.POST, request.FILES, instance=surat)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                aksi='updated',
                deskripsi=f"Surat Masuk: {surat.nomor_surat} - {surat.perihal}",
                user=request.user,
            )
            messages.success(request, 'Surat masuk berhasil diperbarui.')
            return redirect('persuratan:surat_masuk_list')
    else:
        form = SuratMasukForm(instance=surat)

    context = {'form': form, 'surat': surat, 'judul': 'Edit Surat Masuk', 'subjudul': surat.nomor_surat, 'is_edit': True}
    return render(request, 'persuratan/surat_masuk_form.html', context)


@login_required
def surat_masuk_detail(request, pk):
    surat = get_object_or_404(SuratMasuk, pk=pk)
    return render(request, 'persuratan/surat_masuk_detail.html', {'surat': surat})


@login_required
def surat_masuk_delete(request, pk):
    if not is_umum_or_kasubag(request.user):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('dashboard')

    surat = get_object_or_404(SuratMasuk, pk=pk)
    if request.method == 'POST':
        ActivityLog.objects.create(
            aksi='deleted',
            deskripsi=f"Surat Masuk: {surat.nomor_surat} - {surat.perihal}",
            user=request.user,
        )
        surat.delete()
        messages.success(request, 'Surat masuk berhasil dihapus.')
    return redirect('persuratan:surat_masuk_list')


# ===== SURAT KELUAR =====

@login_required
def surat_keluar_list(request):
    if not is_umum_or_kasubag(request.user):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('dashboard')

    query = request.GET.get('q', '')
    daftar_surat = SuratKeluar.objects.all()

    if query:
        daftar_surat = daftar_surat.filter(
            Q(nomor_surat__icontains=query) |
            Q(tujuan_surat__icontains=query) |
            Q(perihal__icontains=query)
        )

    context = {
        'daftar_surat': daftar_surat,
        'query': query,
        'jumlah_surat': daftar_surat.count(),
    }
    return render(request, 'persuratan/surat_keluar_list.html', context)


@login_required
def surat_keluar_create(request):
    if not is_umum_or_kasubag(request.user):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = SuratKeluarForm(request.POST, request.FILES)
        if form.is_valid():
            surat = form.save(commit=False)
            surat.dibuat_oleh = request.user
            surat.save()
            ActivityLog.objects.create(
                aksi='created',
                deskripsi=f"Surat Keluar: {surat.nomor_surat} - {surat.perihal}",
                user=request.user,
            )
            messages.success(request, 'Surat keluar berhasil dicatat.')
            return redirect('persuratan:surat_keluar_list')
    else:
        form = SuratKeluarForm()

    context = {'form': form, 'judul': 'Tambah Surat Keluar', 'subjudul': 'Catat surat keluar baru', 'is_edit': False}
    return render(request, 'persuratan/surat_keluar_form.html', context)


@login_required
def surat_keluar_update(request, pk):
    if not is_umum_or_kasubag(request.user):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('dashboard')

    surat = get_object_or_404(SuratKeluar, pk=pk)

    if request.method == 'POST':
        form = SuratKeluarForm(request.POST, request.FILES, instance=surat)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                aksi='updated',
                deskripsi=f"Surat Keluar: {surat.nomor_surat} - {surat.perihal}",
                user=request.user,
            )
            messages.success(request, 'Surat keluar berhasil diperbarui.')
            return redirect('persuratan:surat_keluar_list')
    else:
        form = SuratKeluarForm(instance=surat)

    context = {'form': form, 'surat': surat, 'judul': 'Edit Surat Keluar', 'subjudul': surat.nomor_surat, 'is_edit': True}
    return render(request, 'persuratan/surat_keluar_form.html', context)


@login_required
def surat_keluar_detail(request, pk):
    surat = get_object_or_404(SuratKeluar, pk=pk)
    return render(request, 'persuratan/surat_keluar_detail.html', {'surat': surat})


@login_required
def surat_keluar_delete(request, pk):
    if not is_umum_or_kasubag(request.user):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('dashboard')

    surat = get_object_or_404(SuratKeluar, pk=pk)
    if request.method == 'POST':
        ActivityLog.objects.create(
            aksi='deleted',
            deskripsi=f"Surat Keluar: {surat.nomor_surat} - {surat.perihal}",
            user=request.user,
        )
        surat.delete()
        messages.success(request, 'Surat keluar berhasil dihapus.')
    return redirect('persuratan:surat_keluar_list')