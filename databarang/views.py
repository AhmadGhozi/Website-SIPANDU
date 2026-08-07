from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import BarangATK
from .forms import BarangATKForm
from dashboard.models import ActivityLog


@login_required
def barang_list(request):
    query = request.GET.get('q', '')
    daftar_barang = BarangATK.objects.all()

    if query:
        daftar_barang = daftar_barang.filter(
            Q(kode_barang__icontains=query) | Q(nama_barang__icontains=query)
        )

    context = {
        'daftar_barang': daftar_barang,
        'query': query,
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