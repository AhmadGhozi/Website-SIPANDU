from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta


class Asset(models.Model):
    KONDISI_CHOICES = [
        ('baik', 'Baik'),
        ('kurang_baik', 'Kurang Baik'),
        ('rusak', 'Rusak'),
    ]

    KATEGORI_CHOICES = [
        ('kendaraan', 'Kendaraan'),
        ('elektronik', 'Elektronik'),
        ('lainnya', 'Lainnya'),
    ]

    LOKASI_CHOICES = [
        ('Ruang Tamu DPPKB', 'Ruang Tamu DPPKB'),
        ('Bagian Umum dan Kepegawaian DPPKB', 'Bagian Umum dan Kepegawaian DPPKB'),
        ('Ruang Kepala Dinas DPPKB', 'Ruang Kepala Dinas DPPKB'),
        ('Ruang Alat Kontrasepsi DPPKB', 'Ruang Alat Kontrasepsi DPPKB'),
        ('Sekretariat Genre DPPKB', 'Sekretariat Genre DPPKB'),
        ('Mushollah DPPKB', 'Mushollah DPPKB'),
        ('Dapur DPPKB', 'Dapur DPPKB'),
        ('Aula Bangga Kencana DPPKB', 'Aula Bangga Kencana DPPKB'),
        ('Gudang DPPKB', 'Gudang DPPKB'),
        ('Bagian Perencanaan Program & Keuangan DPPKB', 'Bagian Perencanaan Program & Keuangan DPPKB'),
        ('Ruang Sekretaris DPPKB', 'Ruang Sekretaris DPPKB'),
        ('Bidang KB DPPKB', 'Bidang KB DPPKB'),
        ('Bidang DaldukP2 DPPKB', 'Bidang DaldukP2 DPPKB'),
        ('Bidang K3 DPPKB', 'Bidang K3 DPPKB'),
        ('Ruang Kepala Bidang K3 DPPKB', 'Ruang Kepala Bidang K3 DPPKB'),
        ('Balai Loa Janan Ilir', 'Balai Loa Janan Ilir'),
        ('Balai Palaran', 'Balai Palaran'),
        ('Balai Samarinda Ilir', 'Balai Samarinda Ilir'),
        ('Balai Samarinda Kota', 'Balai Samarinda Kota'),
        ('Balai Samarinda Seberang', 'Balai Samarinda Seberang'),
        ('Balai Samarinda Ulu', 'Balai Samarinda Ulu'),
        ('Balai Samarinda Utara', 'Balai Samarinda Utara'),
        ('Balai Sambutan', 'Balai Sambutan'),
        ('Balai Sungai Kunjang', 'Balai Sungai Kunjang'),
        ('Balai Sungai Pinang', 'Balai Sungai Pinang'),
]

    kategori = models.CharField(max_length=15, choices=KATEGORI_CHOICES, default='lainnya')
    kode_barang = models.CharField(max_length=30, verbose_name="Kode Barang")
    nama_barang = models.CharField(max_length=150, verbose_name="Nama Barang")
    merk_type = models.CharField(max_length=150, verbose_name="Merk / Type")
    jumlah = models.PositiveIntegerField(default=0)
    harga_satuan = models.DecimalField(max_digits=15, decimal_places=2)
    kondisi = models.CharField(max_length=15, choices=KONDISI_CHOICES, default='baik')
    keterangan = models.TextField(blank=True, null=True, verbose_name="Keterangan")
    lokasi = models.CharField(max_length=100, choices=LOKASI_CHOICES, blank=True, verbose_name="Lokasi")
    pengguna = models.CharField(max_length=150, blank=True, verbose_name="Pengguna/Pemegang Saat Ini")

    register = models.CharField(max_length=20, blank=True, verbose_name="Register")
    tahun_pembelian = models.PositiveIntegerField(blank=True, null=True, verbose_name="Tahun Pembelian")
    nomor_identitas = models.CharField(max_length=255, blank=True, verbose_name="No. Sertifikat/Pabrik/Chasis/Mesin")

    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diperbarui_pada = models.DateTimeField(auto_now=True)

    tanggal_jatuh_tempo_pajak = models.DateField(blank=True, null=True, verbose_name="Tanggal Jatuh Tempo Pajak")

    class Meta:
        ordering = ['kode_barang']
        verbose_name = "Asset"
        verbose_name_plural = "Asset"
        unique_together = ['kode_barang', 'register']

    def __str__(self):
        return f"{self.kode_barang} - {self.nama_barang}"

    @property
    def total_nilai(self):
        return self.jumlah * self.harga_satuan

    @property
    def status_ganti_oli(self):
        riwayat_oli = self.riwayat_service.filter(jenis_service__icontains='oli').order_by('-tanggal').first()
        if not riwayat_oli:
            return {'status': 'belum_ada', 'terakhir': None, 'berikutnya': None}
        
        berikutnya = riwayat_oli.tanggal + timedelta(days=182)
        hari_ini = date.today()
        selisih = (berikutnya - hari_ini).days

        if selisih < 0:
            status = 'terlambat'
        elif selisih <= 30:
            status = 'mendekati'
        else:
            status = 'aman'

        return {'status': status, 'terakhir': riwayat_oli.tanggal, 'berikutnya': berikutnya}


    @property
    def status_pajak(self):
        if not self.tanggal_jatuh_tempo_pajak:
            return {'status': 'belum_diisi'}

        hari_ini = date.today()
        selisih = (self.tanggal_jatuh_tempo_pajak - hari_ini).days

        if selisih < 0:
            status = 'terlambat'
        elif selisih <= 30:
            status = 'mendekati'
        else:
            status = 'aman'

        return {'status': status}

class PermintaanService(models.Model):
    STATUS_CHOICES = [
        ('diajukan', 'Diajukan'),
        ('disetujui', 'Disetujui'),
        ('ditolak', 'Ditolak'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='permintaan_service')
    jenis_service = models.CharField(max_length=150, verbose_name="Jenis Service/Pemeliharaan")
    keterangan = models.TextField(blank=True, verbose_name="Keterangan/Alasan Pengajuan")
    biaya_estimasi = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='diajukan')
    catatan_approval = models.TextField(blank=True)

    diajukan_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='service_diajukan')
    diajukan_pada = models.DateTimeField(auto_now_add=True)

    diproses_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_diproses')
    diproses_pada = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-diajukan_pada']
        verbose_name = "Permintaan Service"
        verbose_name_plural = "Permintaan Service"

    def __str__(self):
        return f"{self.jenis_service} - {self.asset.nama_barang}"

    @property
    def badge_class(self):
        return {
            'diajukan': 'bg-warning-subtle text-warning',
            'disetujui': 'bg-success-subtle text-success',
            'ditolak': 'bg-danger-subtle text-danger',
        }.get(self.status, 'bg-secondary-subtle text-secondary')

class RiwayatService(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='riwayat_service')
    permintaan = models.OneToOneField(PermintaanService, on_delete=models.SET_NULL, null=True, blank=True, related_name='riwayat')
    tanggal = models.DateField()
    jenis_service = models.CharField(max_length=150, verbose_name="Jenis Service/Pemeliharaan")
    keterangan = models.TextField(blank=True)
    biaya = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    dibuat_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    dibuat_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-tanggal', '-dibuat_pada']
        verbose_name = "Riwayat Service"
        verbose_name_plural = "Riwayat Service"

    def __str__(self):
        return f"{self.jenis_service} - {self.asset.nama_barang} ({self.tanggal})"
    
class PindahTanganAsset(models.Model):
    STATUS_CHOICES = [
        ('diajukan', 'Menunggu Persetujuan'),
        ('disetujui', 'Disetujui'),
        ('ditolak', 'Ditolak'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='pindah_tangan')

    nama_pihak_pertama = models.CharField(max_length=150, blank=True)
    lokasi_pihak_pertama = models.CharField(max_length=100, blank=True)

    nama_pihak_kedua = models.CharField(max_length=150, verbose_name="Diserahkan Kepada")
    lokasi_pihak_kedua = models.CharField(max_length=100, choices=Asset.LOKASI_CHOICES, verbose_name="Lokasi Tujuan")

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='diajukan')
    catatan_approval = models.TextField(blank=True)

    diajukan_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='pindah_tangan_diajukan')
    diajukan_pada = models.DateTimeField(auto_now_add=True)

    diproses_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pindah_tangan_diproses')
    diproses_pada = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-diajukan_pada']
        verbose_name = "Pindah Tangan Asset"
        verbose_name_plural = "Pindah Tangan Asset"

    def __str__(self):
        return f"Pindah Tangan {self.asset.nama_barang} ke {self.nama_pihak_kedua}"

    @property
    def badge_class(self):
        return {
            'diajukan': 'bg-warning-subtle text-warning',
            'disetujui': 'bg-success-subtle text-success',
            'ditolak': 'bg-danger-subtle text-danger',
        }.get(self.status, 'bg-secondary-subtle text-secondary')