from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Asset
from .forms import AssetForm
import qrcode
import io
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdf_canvas
from dashboard.models import ActivityLog
from .models import Asset, RiwayatService, PermintaanService
from .forms import AssetForm, PermintaanServiceForm, ApprovalServiceForm, EditPermintaanServiceForm

@login_required
def asset_list(request):
    query = request.GET.get('q', '')
    daftar_asset = Asset.objects.all()

    # Filter khusus akun Balai/Bidang: cuma lihat asset di unit mereka sendiri
    profile = getattr(request.user, 'profile', None)
    is_balai_bidang = profile and profile.jenis_akun in ['balai', 'bidang']
    if is_balai_bidang:
        daftar_asset = daftar_asset.filter(lokasi=profile.unit_kerja)

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
        'is_balai_bidang': is_balai_bidang,
    }
    return render(request, 'asset/asset_list.html', context)

@login_required
def asset_create(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            asset = form.save()
            ActivityLog.objects.create(
                aksi='created',
                deskripsi=f"{asset.nama_barang} ({asset.kode_barang})",
                user=request.user,
            )
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

@login_required
def asset_update(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            asset = form.save()
            ActivityLog.objects.create(
                aksi='updated',
                deskripsi=f"{asset.nama_barang} ({asset.kode_barang})",
                user=request.user,
            )
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

@login_required
def asset_delete(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        ActivityLog.objects.create(
            aksi='deleted',
            deskripsi=f"{asset.nama_barang} ({asset.kode_barang})",
            user=request.user,
        )
        asset.delete()
        messages.success(request, 'Asset berhasil dihapus.')
        return redirect('asset:asset_list')

    return render(request, 'asset/asset_confirm_delete.html', {'asset': asset})

@login_required
def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    return render(request, 'asset/asset_detail.html', {'asset': asset})

def asset_public_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    return render(request, 'asset/asset_public_detail.html', {'asset': asset})

@login_required
def asset_qrcode(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    detail_url = request.build_absolute_uri(
        reverse('asset:asset_public_detail', args=[asset.pk])
        )

    qr = qrcode.make(detail_url)
    buffer = io.BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = f'inline; filename="qr-{asset.kode_barang}.png"'
    return response

@login_required
@require_POST
def asset_qrcode_massal(request):
    ids = request.POST.getlist('asset_ids')
    assets = Asset.objects.filter(pk__in=ids)

    if not assets:
        messages.warning(request, 'Pilih minimal 1 asset untuk dicetak QR Code-nya.')
        return redirect('asset:asset_list')

    buffer = io.BytesIO()
    page_width, page_height = A4
    c = pdf_canvas.Canvas(buffer, pagesize=A4)

    margin = 10 * mm
    label_w = 60 * mm
    label_h = 40 * mm
    cols = 3
    gap = 5 * mm

    x_start = margin
    y_start = page_height - margin - label_h
    x, y = x_start, y_start
    col_count = 0

    for asset in assets:
        detail_url = request.build_absolute_uri(reverse('asset:asset_public_detail', args=[asset.pk]))
        qr_img = qrcode.make(detail_url)
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_reader = ImageReader(qr_buffer)

        # Kotak border label (biar gampang digunting)
        c.rect(x, y, label_w, label_h)

        # Nama instansi kecil di atas
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(x + label_w / 2, y + label_h - 5 * mm, "SIPANDU-KB")

        # QR Code
        qr_size = 26 * mm
        qr_x = x + (label_w - qr_size) / 2
        qr_y = y + label_h - qr_size - 8 * mm
        c.drawImage(qr_reader, qr_x, qr_y, width=qr_size, height=qr_size)

        # Kode barang
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + label_w / 2, y + 5.5 * mm, asset.kode_barang)

        # Nama barang (dipotong kalau kepanjangan)
        c.setFont("Helvetica", 7)
        nama = asset.nama_barang[:28]
        c.drawCentredString(x + label_w / 2, y + 2 * mm, nama)

        col_count += 1
        if col_count >= cols:
            col_count = 0
            x = x_start
            y -= label_h + gap
        else:
            x += label_w + gap

        if y < margin:
            c.showPage()
            x, y = x_start, y_start
            col_count = 0

    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="qr-code-asset.pdf"'
    return response

def is_kasubag_umum(user):
    return hasattr(user, 'profile') and user.profile.role == 'kasubag_umum'


@login_required
def asset_service_list(request, pk):
    """Riwayat service (read-only) untuk 1 asset tertentu."""
    asset = get_object_or_404(Asset, pk=pk)
    riwayat = asset.riwayat_service.all()
    permintaan_list = asset.permintaan_service.all()
    return render(request, 'asset/asset_service_list.html', {
        'asset': asset, 'riwayat': riwayat, 'permintaan_list': permintaan_list,
    })

@login_required
def permintaan_service_create(request):
    if request.method == 'POST':
        form = PermintaanServiceForm(request.POST, user=request.user)
        if form.is_valid():
            asset = form.cleaned_data['asset']
            permintaan = PermintaanService.objects.create(
                asset=asset,
                jenis_service=form.cleaned_data['jenis_service'],
                keterangan=form.cleaned_data['keterangan'],
                biaya_estimasi=form.cleaned_data['biaya_estimasi'],
                diajukan_oleh=request.user,
            )
            messages.success(request, f'Permintaan service untuk "{asset.nama_barang}" berhasil diajukan.')
            return redirect('asset:permintaan_service_list')
    else:
        form = PermintaanServiceForm(user=request.user)

    return render(request, 'asset/permintaan_service_form.html', {'form': form})


@login_required
def permintaan_service_list(request):
    permintaan_list = PermintaanService.objects.select_related('asset', 'diajukan_oleh').all()

    # Filter khusus akun Balai/Bidang: cuma lihat permintaan untuk asset di unit mereka sendiri
    profile = getattr(request.user, 'profile', None)
    if profile and profile.jenis_akun in ['balai', 'bidang']:
        permintaan_list = permintaan_list.filter(asset__lokasi=profile.unit_kerja)

    context = {
        'permintaan_list': permintaan_list,
        'is_approver': is_kasubag_umum(request.user),
        'total_diajukan': permintaan_list.filter(status='diajukan').count(),
        'total_disetujui': permintaan_list.filter(status='disetujui').count(),
        'total_ditolak': permintaan_list.filter(status='ditolak').count(),
    }
    return render(request, 'asset/permintaan_service_list.html', context)


@login_required
def permintaan_service_detail(request, pk):
    permintaan = get_object_or_404(PermintaanService, pk=pk)
    is_approver = is_kasubag_umum(request.user)
    form = ApprovalServiceForm()

    if request.method == 'POST':
        if not is_approver:
            messages.error(request, 'Anda tidak memiliki akses untuk memproses permintaan ini.')
            return redirect('asset:permintaan_service_detail', pk=permintaan.pk)

        aksi = request.POST.get('aksi')

        if aksi == 'tolak':
            permintaan.status = 'ditolak'
            permintaan.catatan_approval = request.POST.get('catatan_approval', '')
            permintaan.diproses_oleh = request.user
            permintaan.diproses_pada = timezone.now()
            permintaan.save()
            messages.success(request, 'Permintaan service ditolak.')
            return redirect('asset:permintaan_service_list')

        elif aksi == 'setuju':
            form = ApprovalServiceForm(request.POST)
            if form.is_valid():
                permintaan.status = 'disetujui'
                permintaan.catatan_approval = form.cleaned_data['catatan_approval']
                permintaan.diproses_oleh = request.user
                permintaan.diproses_pada = timezone.now()
                permintaan.save()

                RiwayatService.objects.create(
                    asset=permintaan.asset,
                    permintaan=permintaan,
                    tanggal=form.cleaned_data['tanggal_pelaksanaan'],
                    jenis_service=permintaan.jenis_service,
                    keterangan=permintaan.keterangan,
                    biaya=form.cleaned_data['biaya_aktual'] or permintaan.biaya_estimasi,
                    dibuat_oleh=request.user,
                )
                messages.success(request, 'Permintaan service disetujui dan riwayat berhasil dicatat.')
                return redirect('asset:permintaan_service_list')

    return render(request, 'asset/permintaan_service_detail.html', {
        'permintaan': permintaan, 'is_approver': is_approver, 'form': form,
    })

@login_required
def permintaan_service_update(request, pk):
    permintaan = get_object_or_404(PermintaanService, pk=pk)

    # Cuma boleh diedit kalau masih status "diajukan"
    if permintaan.status != 'diajukan':
        messages.error(request, 'Permintaan yang sudah diproses tidak dapat diubah.')
        return redirect('asset:permintaan_service_detail', pk=permintaan.pk)

    # Cuma pengaju sendiri atau admin yang boleh edit
    if permintaan.diajukan_oleh != request.user and not request.user.is_superuser:
        messages.error(request, 'Anda tidak memiliki akses untuk mengubah permintaan ini.')
        return redirect('asset:permintaan_service_detail', pk=permintaan.pk)

    if request.method == 'POST':
        form = EditPermintaanServiceForm(request.POST, instance=permintaan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Permintaan service berhasil diperbarui.')
            return redirect('asset:permintaan_service_detail', pk=permintaan.pk)
    else:
        form = EditPermintaanServiceForm(instance=permintaan)

    return render(request, 'asset/permintaan_service_edit.html', {'form': form, 'permintaan': permintaan})


@login_required
def permintaan_service_delete(request, pk):
    permintaan = get_object_or_404(PermintaanService, pk=pk)

    if permintaan.status != 'diajukan':
        messages.error(request, 'Permintaan yang sudah diproses tidak dapat dihapus.')
        return redirect('asset:permintaan_service_detail', pk=permintaan.pk)

    if permintaan.diajukan_oleh != request.user and not request.user.is_superuser:
        messages.error(request, 'Anda tidak memiliki akses untuk menghapus permintaan ini.')
        return redirect('asset:permintaan_service_detail', pk=permintaan.pk)

    if request.method == 'POST':
        permintaan.delete()
        messages.success(request, 'Permintaan service berhasil dibatalkan.')
        return redirect('asset:permintaan_service_list')

    return redirect('asset:permintaan_service_detail', pk=permintaan.pk)