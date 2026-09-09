import io
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import SuratMasuk, SuratKeluar, Disposisi
from .forms import SuratMasukForm, SuratKeluarForm, DisposisiForm
from dashboard.models import ActivityLog
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from asset.views import build_kop_surat


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

# ===== DISPOSISI =====

def is_tujuan_disposisi(user, disposisi):
    profile = getattr(user, 'profile', None)
    if not profile:
        return False
    return profile.unit_kerja in disposisi.unit_tujuan


@login_required
def disposisi_list(request):
    profile = getattr(request.user, 'profile', None)

    if profile and is_umum_or_kasubag(request.user):
        daftar_disposisi = Disposisi.objects.all()
    elif profile:
        daftar_disposisi = Disposisi.objects.filter(unit_tujuan__contains=profile.unit_kerja)
    else:
        daftar_disposisi = Disposisi.objects.none()

    context = {'daftar_disposisi': daftar_disposisi}
    return render(request, 'persuratan/disposisi_list.html', context)


@login_required
def disposisi_create(request, surat_pk):
    if not is_umum_or_kasubag(request.user):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('dashboard')

    surat = get_object_or_404(SuratMasuk, pk=surat_pk)

    if request.method == 'POST':
        form = DisposisiForm(request.POST)
        if form.is_valid():
            disposisi = form.save(commit=False)
            disposisi.surat_masuk = surat
            disposisi.dibuat_oleh = request.user
            disposisi.save()
            ActivityLog.objects.create(
                aksi='created',
                deskripsi=f"Disposisi surat: {surat.nomor_surat}",
                user=request.user,
            )
            messages.success(request, 'Disposisi berhasil dibuat.')
            return redirect('persuratan:disposisi_detail', pk=disposisi.pk)
    else:
        form = DisposisiForm()

    context = {'form': form, 'surat': surat}
    return render(request, 'persuratan/disposisi_form.html', context)


@login_required
def disposisi_detail(request, pk):
    disposisi = get_object_or_404(Disposisi, pk=pk)
    bisa_tindak_lanjut = is_tujuan_disposisi(request.user, disposisi) and disposisi.status == 'menunggu'
    context = {'disposisi': disposisi, 'bisa_tindak_lanjut': bisa_tindak_lanjut}
    return render(request, 'persuratan/disposisi_detail.html', context)


@login_required
def disposisi_tindak_lanjut(request, pk):
    disposisi = get_object_or_404(Disposisi, pk=pk)

    if not is_tujuan_disposisi(request.user, disposisi):
        messages.error(request, 'Anda tidak memiliki akses untuk menindaklanjuti disposisi ini.')
        return redirect('persuratan:disposisi_detail', pk=pk)

    if request.method == 'POST':
        disposisi.status = 'ditindaklanjuti'
        disposisi.ditindaklanjuti_oleh = request.user
        disposisi.tanggal_tindak_lanjut = timezone.now()
        disposisi.save()
        ActivityLog.objects.create(
            aksi='updated',
            deskripsi=f"Tindak lanjut disposisi: {disposisi.surat_masuk.nomor_surat}",
            user=request.user,
        )
        messages.success(request, 'Disposisi berhasil ditandai sebagai ditindaklanjuti.')

    return redirect('persuratan:disposisi_detail', pk=pk)

@login_required
def disposisi_pdf(request, pk):
    disposisi = get_object_or_404(Disposisi, pk=pk)
    surat = disposisi.surat_masuk

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleCustom', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=16)
    label_style = ParagraphStyle('LabelStyle', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold')
    value_style = ParagraphStyle('ValueStyle', parent=styles['Normal'], fontSize=10)

    elements = []
    elements.extend(build_kop_surat(styles))
    elements.append(Paragraph("LEMBAR DISPOSISI", title_style))
    elements.append(Spacer(1, 16))

    # Tabel info surat
    info_data = [
        [Paragraph("Surat Dari", label_style), Paragraph(surat.asal_surat, value_style),
         Paragraph("Nomor Surat", label_style), Paragraph(surat.nomor_surat, value_style)],
        [Paragraph("Tanggal Surat", label_style), Paragraph(surat.tanggal_surat.strftime('%d %B %Y'), value_style),
         Paragraph("Nomor Agenda", label_style), Paragraph(surat.nomor_agenda, value_style)],
        [Paragraph("Diterima Tanggal", label_style), Paragraph(surat.tanggal_diterima.strftime('%d %B %Y'), value_style),
         Paragraph("Sifat", label_style), Paragraph(surat.get_sifat_display(), value_style)],
    ]
    info_table = Table(info_data, colWidths=[3*cm, 5.5*cm, 3*cm, 5.5*cm])
    info_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)

    # Perihal
    perihal_table = Table(
        [[Paragraph("Perihal", label_style), Paragraph(surat.perihal, value_style)]],
        colWidths=[3*cm, 14*cm],
    )
    perihal_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('LINEABOVE', (0, 0), (-1, 0), 0, colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
    ]))
    elements.append(perihal_table)
    elements.append(Spacer(1, 4))

    # Ditujukan Kepada
    unit_text = "<br/>".join([f"☑ {u}" for u in disposisi.unit_tujuan]) or "-"
    tujuan_table = Table(
        [[Paragraph("Ditujukan Kepada", label_style), Paragraph(unit_text, value_style)]],
        colWidths=[3*cm, 14*cm],
    )
    tujuan_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(tujuan_table)
    elements.append(Spacer(1, 4))

    # Instruksi/Informasi
    instruksi_text = "<br/>".join([f"☑ {label}" for label in disposisi.label_instruksi]) or "-"
    if disposisi.catatan:
        instruksi_text += f"<br/><br/><b>Catatan:</b> {disposisi.catatan}"

    instruksi_table = Table(
        [[Paragraph("Instruksi/Informasi", label_style), Paragraph(instruksi_text, value_style)]],
        colWidths=[3*cm, 14*cm],
    )
    instruksi_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 30),
    ]))
    elements.append(instruksi_table)
    elements.append(Spacer(1, 4))

    # Paraf
    paraf_table = Table(
        [[Paragraph("Paraf", label_style)], [Spacer(1, 40)]],
        colWidths=[17*cm],
    )
    paraf_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(paraf_table)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="disposisi_{surat.nomor_surat}.pdf"'
    return response