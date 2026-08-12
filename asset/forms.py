from django import forms
from .models import Asset, RiwayatService, PermintaanService


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'kode_barang', 'nama_barang', 'merk_type', 'jumlah', 'harga_satuan',
            'kondisi', 'lokasi', 'pengguna', 'keterangan',
            'register', 'tahun_pembelian', 'nomor_identitas',
        ]
        widgets = {
            'kode_barang': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1.1.1.11.111.111.111'}),
            'nama_barang': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama asset'}),
            'merk_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Dell / Latitude 5520'}),
            'jumlah': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_jumlah'}),
            'harga_satuan': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_harga_satuan'}),
            'kondisi': forms.Select(attrs={'class': 'd-none'}),
            'lokasi': forms.Select(attrs={'class': 'd-none'}),
            'pengguna': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama pemegang saat ini (opsional)'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Catatan tambahan (opsional)'}),
            'register': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 000002'}),
            'tahun_pembelian': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 2024'}),
            'nomor_identitas': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'No. Sertifikat/Pabrik/Chasis/Mesin (khusus kendaraan)'}),
        }

    def clean_kode_barang(self):
        kode_barang = self.cleaned_data['kode_barang']
        qs = Asset.objects.filter(kode_barang=kode_barang)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Kode barang ini sudah digunakan. Silakan gunakan kode lain.')
        return kode_barang


class PermintaanServiceForm(forms.Form):
    kode_barang = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 1.3.2.05.001.004.001'})
    )
    register = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 000002'})
    )
    jenis_service = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Ganti Oli, Service AC, Perbaikan Layar'})
    )
    keterangan = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Jelaskan kondisi/alasan pengajuan'})
    )
    biaya_estimasi = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Opsional'})
    )

    def clean(self):
        cleaned_data = super().clean()
        kode_barang = cleaned_data.get('kode_barang')
        register = cleaned_data.get('register')

        if kode_barang and register:
            try:
                asset = Asset.objects.get(kode_barang=kode_barang, register=register)
                cleaned_data['asset'] = asset
            except Asset.DoesNotExist:
                raise forms.ValidationError('Asset dengan Kode Barang dan No. Register tersebut tidak ditemukan. Periksa kembali data yang dimasukkan.')

        return cleaned_data

class ApprovalServiceForm(forms.Form):
    tanggal_pelaksanaan = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    biaya_aktual = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Opsional'})
    )
    catatan_approval = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Catatan (opsional)'})
    )