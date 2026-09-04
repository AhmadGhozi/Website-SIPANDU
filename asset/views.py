import os
from django.conf import settings
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
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdf_canvas
from dashboard.models import ActivityLog
from .models import Asset, RiwayatService, PermintaanService, PindahTanganAsset
from .forms import AssetForm, PermintaanServiceForm, ApprovalServiceForm, EditPermintaanServiceForm, PindahTanganForm

def build_kop_surat(styles):
    """
    Mengembalikan list elemen reportlab (logo + teks instansi + garis pembatas)
    untuk dipasang di bagian paling atas dokumen PDF.
    """
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo_samarinda.png')

    kop_normal = ParagraphStyle(
        'KopNormal', parent=styles['Normal'],
        alignment=TA_CENTER, fontSize=12, leading=14,
    )
    kop_bold = ParagraphStyle(
        'KopBold', parent=styles['Normal'],
        alignment=TA_CENTER, fontSize=11.5, leading=13, fontName='Helvetica-Bold',
    )
    kop_kecil = ParagraphStyle(
        'KopKecil', parent=styles['Normal'],
        alignment=TA_CENTER, fontSize=8.5, leading=11,
    )

    teks_kop = [
        Paragraph("PEMERINTAH KOTA SAMARINDA", kop_normal),
        Paragraph("DINAS PENGENDALIAN PENDUDUK DAN KELUARGA BERENCANA", kop_bold),
        Paragraph("Jalan Milono No. 1 Kelurahan Bugis Kec. Samarinda Kota, Samarinda 75121", kop_kecil),
        Paragraph("Website : dppkb.samarindakota.go.id &nbsp;&nbsp; Email. Dppkb.kotasmarinda2020@gmail.com", kop_kecil),
    ]

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2.1*cm, height=2.1*cm)
    else:
        logo = Paragraph("", styles['Normal'])

    kop_table = Table(
        [[logo, teks_kop]],
        colWidths=[2.5*cm, 14.5*cm],
    )
    kop_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('LEFTPADDING', (0, 0), (0, 0), 0),
        ('RIGHTPADDING', (1, 0), (1, 0), 0),
    ]))

    elements = [
        kop_table,
        Spacer(1, 8),
        HRFlowable(width="100%", thickness=2, color=colors.black, spaceAfter=2),
        HRFlowable(width="100%", thickness=0.75, color=colors.black, spaceAfter=4),
        Spacer(1, 14),
    ]
    return elements

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
    return render(request, 'asset/asset_detail.html', {'asset': asset, 'is_admin': is_admin(request.user)})

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

def is_umum_or_kasubag(user):
    profile = getattr(user, 'profile', None)
    if not profile:
        return False
    return profile.jenis_akun == 'umum' or profile.role == 'kasubag_umum'


@login_required
def perencanaan_service_list(request):
    if not is_umum_or_kasubag(request.user):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('dashboard')

    kendaraan = Asset.objects.filter(kategori='kendaraan')

    data = []
    for asset in kendaraan:
        data.append({
            'asset': asset,
            'oli': asset.status_ganti_oli,
            'pajak': asset.status_pajak,
        })

    context = {
        'data': data,
        'total_kendaraan': kendaraan.count(),
        'total_perlu_perhatian': sum(
            1 for d in data
            if d['oli']['status'] in ['mendekati', 'terlambat'] or d['pajak']['status'] in ['mendekati', 'terlambat']
        ),
    }
    return render(request, 'asset/perencanaan_service_list.html', context)

def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin'

@login_required
def pindah_tangan_create(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Hanya Admin yang dapat memproses pindah tangan asset.')
        return redirect('asset:asset_detail', pk=pk)

    asset = get_object_or_404(Asset, pk=pk)

    if request.method == 'POST':
        form = PindahTanganForm(request.POST)
        if form.is_valid():
            pt = form.save(commit=False)
            pt.asset = asset
            pt.nama_pihak_pertama = asset.pengguna
            pt.lokasi_pihak_pertama = asset.lokasi
            pt.diajukan_oleh = request.user
            pt.save()
            messages.success(request, 'Pengajuan pindah tangan berhasil dikirim, menunggu persetujuan Kasubag Umum.')
            return redirect('asset:pindah_tangan_list')
    else:
        form = PindahTanganForm()

    return render(request, 'asset/pindah_tangan_form.html', {'form': form, 'asset': asset})


@login_required
def pindah_tangan_list(request):
    if not (is_admin(request.user) or is_kasubag_umum(request.user)):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('dashboard')

    daftar = PindahTanganAsset.objects.select_related('asset', 'diajukan_oleh').all()

    context = {
        'daftar': daftar,
        'is_approver': is_kasubag_umum(request.user),
        'total_diajukan': daftar.filter(status='diajukan').count(),
        'total_disetujui': daftar.filter(status='disetujui').count(),
        'total_ditolak': daftar.filter(status='ditolak').count(),
    }
    return render(request, 'asset/pindah_tangan_list.html', context)


@login_required
def pindah_tangan_detail(request, pk):
    if not (is_admin(request.user) or is_kasubag_umum(request.user)):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('dashboard')
    
    pt = get_object_or_404(PindahTanganAsset, pk=pk)
    is_approver = is_kasubag_umum(request.user)

    if request.method == 'POST':
        if not is_approver:
            messages.error(request, 'Anda tidak memiliki akses untuk memproses pengajuan ini.')
            return redirect('asset:pindah_tangan_detail', pk=pt.pk)

        aksi = request.POST.get('aksi')
        catatan = request.POST.get('catatan_approval', '')

        if aksi == 'tolak':
            pt.status = 'ditolak'
            pt.catatan_approval = catatan
            pt.diproses_oleh = request.user
            pt.diproses_pada = timezone.now()
            pt.save()
            messages.success(request, 'Pengajuan pindah tangan ditolak.')
            return redirect('asset:pindah_tangan_list')

        elif aksi == 'setuju':
            asset = pt.asset
            asset.pengguna = pt.nama_pihak_kedua
            asset.lokasi = pt.lokasi_pihak_kedua
            asset.save()

            pt.status = 'disetujui'
            pt.catatan_approval = catatan
            pt.diproses_oleh = request.user
            pt.diproses_pada = timezone.now()
            pt.save()
            messages.success(request, 'Pindah tangan disetujui. Berita Acara siap diunduh.')
            return redirect('asset:pindah_tangan_detail', pk=pt.pk)

    return render(request, 'asset/pindah_tangan_detail.html', {'pt': pt, 'is_approver': is_approver})

def format_tanggal_indonesia(tanggal):
    hari_list = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    bulan_list = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

    hari = hari_list[tanggal.weekday()]
    bulan = bulan_list[tanggal.month - 1]

    return f"{hari}, {tanggal.day:02d} {bulan} {tanggal.year}"

@login_required
def pindah_tangan_pdf(request, pk):
    pt = get_object_or_404(PindahTanganAsset, pk=pk, status='disetujui')
    asset = pt.asset

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleCustom', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=14)
    normal_justify = ParagraphStyle('NormalJustify', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=11, leading=16)

    elements = []
    elements.extend(build_kop_surat(styles))
    elements.append(Paragraph("BERITA ACARA SERAH TERIMA BARANG", title_style))
    elements.append(Spacer(1, 20))

    tanggal_str = format_tanggal_indonesia(pt.diproses_pada) if pt.diproses_pada else '-'
    elements.append(Paragraph(f"Pada hari ini {tanggal_str}, telah dilakukan serah terima barang sebagai berikut:", normal_justify))
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("<b>PIHAK PERTAMA (Yang Menyerahkan):</b>", styles['Normal']))
    elements.append(Paragraph(f"Nama&nbsp;&nbsp;&nbsp;: {pt.nama_pihak_pertama or '-'}", styles['Normal']))
    elements.append(Paragraph(f"Lokasi&nbsp;&nbsp;: {pt.lokasi_pihak_pertama or '-'}", styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>PIHAK KEDUA (Yang Menerima):</b>", styles['Normal']))
    elements.append(Paragraph(f"Nama&nbsp;&nbsp;&nbsp;: {pt.nama_pihak_kedua}", styles['Normal']))
    elements.append(Paragraph(f"Lokasi&nbsp;&nbsp;: {pt.get_lokasi_pihak_kedua_display()}", styles['Normal']))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Barang yang diserahterimakan:", styles['Normal']))
    elements.append(Spacer(1, 8))

    data_tabel = [
        ['No', 'Nama Barang', 'Jumlah', 'Harga'],
        ['1', asset.nama_barang, f"{asset.jumlah} unit", f"Rp {asset.harga_satuan:,.0f}".replace(',', '.')],
    ]
    tabel = Table(data_tabel, colWidths=[1.5*cm, 7*cm, 3*cm, 4*cm])
    tabel.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B2A52')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(tabel)
    elements.append(Spacer(1, 24))

    elements.append(Paragraph(
        "Demikian berita acara serah terima barang ini dibuat oleh kedua belah pihak, adapun "
        "barang tersebut diserahkan dalam keadaan baik dan lengkap. Sejak penandatanganan berita "
        "acara ini, barang tersebut menjadi tanggung jawab Pihak Kedua untuk dipelihara/dirawat "
        "dengan baik serta dipergunakan sesuai keperluan.", normal_justify
    ))
    elements.append(Spacer(1, 40))

    ttd_data = [['Yang Menyerahkan,', 'Yang Menerima,'], ['', ''], ['', ''],
                [f"( {pt.nama_pihak_pertama or '.....................'} )", f"( {pt.nama_pihak_kedua} )"]]
    ttd_table = Table(ttd_data, colWidths=[8*cm, 8*cm])
    ttd_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 1), (-1, 2), 30),
    ]))
    elements.append(ttd_table)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="BAST-{asset.kode_barang}-{pt.pk}.pdf"'
    return response