from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Asset
from .forms import AssetForm


def asset_list(request):
    query = request.GET.get('q', '')
    daftar_asset = Asset.objects.all()

    if query:
        daftar_asset = daftar_asset.filter(
            Q(kode_barang__icontains=query) |
            Q(nama_barang__icontains=query) |
            Q(merk_type__icontains=query)
        )

    context = {
        'daftar_asset': daftar_asset,
        'query': query,
        'jumlah_asset': daftar_asset.count(),
    }
    return render(request, 'asset/asset_list.html', context)


def asset_create(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asset baru berhasil ditambahkan.')
            return redirect('asset:asset_list')
    else:
        form = AssetForm()

    context = {
        'form': form,
        'judul': 'Tambah Asset Baru',
        'subjudul': 'Lengkapi seluruh data asset di bawah ini',
        'is_edit': False,
    }
    return render(request, 'asset/asset_form.html', context)


def asset_update(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data asset berhasil diperbarui.')
            return redirect('asset:asset_list')
    else:
        form = AssetForm(instance=asset)

    context = {
        'form': form,
        'judul': 'Edit Asset',
        'subjudul': f'Kode barang: {asset.kode_barang}',
        'is_edit': True,
        'asset': asset,
    }
    return render(request, 'asset/asset_form.html', context)


def asset_delete(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        asset.delete()
        messages.success(request, 'Asset berhasil dihapus.')
        return redirect('asset:asset_list')

    return render(request, 'asset/asset_confirm_delete.html', {'asset': asset})