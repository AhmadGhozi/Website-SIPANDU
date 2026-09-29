from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Profile
from .forms import PenggunaForm


def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin'


def bisa_lihat_pengguna(user):
    profile = getattr(user, 'profile', None)
    if not profile:
        return False
    return profile.role in ['admin', 'kasubag_umum', 'kadis']


@login_required
def pengguna_list(request):
    if not bisa_lihat_pengguna(request.user):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('dashboard')

    query = request.GET.get('q', '')
    daftar_pengguna = Profile.objects.select_related('user').all()

    if query:
        daftar_pengguna = daftar_pengguna.filter(
            Q(nama_lengkap__icontains=query) |
            Q(jabatan__icontains=query) |
            Q(unit_kerja__icontains=query)
        )

    context = {
        'daftar_pengguna': daftar_pengguna,
        'query': query,
        'total_pengguna': Profile.objects.count(),
        'total_aktif': Profile.objects.filter(status='aktif').count(),
        'total_nonaktif': Profile.objects.filter(status='nonaktif').count(),
    }
    return render(request, 'pengguna/pengguna_list.html', context)


@login_required
def pengguna_create(request):
    if not is_admin(request.user):
        messages.error(request, 'Hanya Admin yang dapat mengakses halaman ini.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = PenggunaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pengguna baru berhasil ditambahkan.')
            return redirect('pengguna:pengguna_list')
    else:
        form = PenggunaForm()

    context = {
        'form': form,
        'judul': 'Tambah Pengguna',
        'subjudul': 'Lengkapi data pengguna baru',
        'is_edit': False,
    }
    return render(request, 'pengguna/pengguna_form.html', context)


@login_required
def pengguna_update(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Hanya Admin yang dapat mengakses halaman ini.')
        return redirect('dashboard')

    profile = get_object_or_404(Profile, pk=pk)

    if request.method == 'POST':
        form = PenggunaForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data pengguna berhasil diperbarui.')
            return redirect('pengguna:pengguna_list')
    else:
        form = PenggunaForm(instance=profile)

    context = {
        'form': form,
        'judul': 'Edit Pengguna',
        'subjudul': f'ID: {profile.id_pengguna}',
        'is_edit': True,
    }
    return render(request, 'pengguna/pengguna_form.html', context)


@login_required
def pengguna_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Hanya Admin yang dapat mengakses halaman ini.')
        return redirect('dashboard')

    profile = get_object_or_404(Profile, pk=pk)
    if request.method == 'POST':
        profile.user.delete()
        messages.success(request, 'Pengguna berhasil dihapus.')
    return redirect('pengguna:pengguna_list')


@login_required
def pengguna_detail(request, pk):
    if not bisa_lihat_pengguna(request.user):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('dashboard')

    profile = get_object_or_404(Profile, pk=pk)
    return render(request, 'pengguna/pengguna_detail.html', {'profile': profile})