from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import PermintaanData
from .forms import PermintaanDataForm, TanggapanPermintaanForm
from dashboard.models import ActivityLog


def is_kasubag_umum(user):
    profile = getattr(user, 'profile', None)
    if not profile:
        return False
    return profile.role == 'kasubag_umum'


def is_tamu(user):
    profile = getattr(user, 'profile', None)
    return bool(profile and profile.role == 'tamu')


@login_required
def permintaan_data_list(request):
    if is_kasubag_umum(request.user):
        daftar_permintaan = PermintaanData.objects.all()
    else:
        daftar_permintaan = PermintaanData.objects.filter(pemohon=request.user)

    context = {'daftar_permintaan': daftar_permintaan}
    return render(request, 'tamu/permintaan_data_list.html', context)


@login_required
def permintaan_data_create(request):
    if not is_tamu(request.user):
        messages.error(request, 'Halaman ini hanya untuk akun Tamu.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = PermintaanDataForm(request.POST)
        if form.is_valid():
            permintaan = form.save(commit=False)
            permintaan.pemohon = request.user
            permintaan.save()
            messages.success(request, 'Permintaan data berhasil diajukan.')
            return redirect('tamu:permintaan_data_list')
    else:
        form = PermintaanDataForm()

    return render(request, 'tamu/permintaan_data_form.html', {'form': form})


@login_required
def permintaan_data_detail(request, pk):
    permintaan = get_object_or_404(PermintaanData, pk=pk)

    bisa_proses = is_kasubag_umum(request.user)

    if not bisa_proses and permintaan.pemohon != request.user:
        messages.error(request, 'Anda tidak memiliki akses ke permintaan ini.')
        return redirect('tamu:permintaan_data_list')

    if bisa_proses and request.method == 'POST':
        form = TanggapanPermintaanForm(request.POST, instance=permintaan)
        if form.is_valid():
            tanggapan = form.save(commit=False)
            tanggapan.diproses_oleh = request.user
            tanggapan.diproses_pada = timezone.now()
            tanggapan.save()
            ActivityLog.objects.create(
                aksi='updated',
                deskripsi=f"Tanggapan Permintaan Data: {permintaan.keperluan} ({permintaan.pemohon.username})",
                user=request.user,
            )
            messages.success(request, 'Tanggapan berhasil disimpan.')
            return redirect('tamu:permintaan_data_detail', pk=pk)
    else:
        form = TanggapanPermintaanForm(instance=permintaan)

    context = {'permintaan': permintaan, 'form': form, 'bisa_proses': bisa_proses}
    return render(request, 'tamu/permintaan_data_detail.html', context)