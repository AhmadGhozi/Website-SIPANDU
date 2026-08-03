from django import forms
from .models import Asset


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['kode_barang', 'nama_barang', 'merk_type', 'jumlah', 'harga_satuan', 'kondisi', 'lokasi', 'pengguna', 'keterangan']
        widgets = {
            'kode_barang': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1.1.1.11.111.111.111'}),
            'nama_barang': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama asset'}),
            'merk_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Dell / Latitude 5520'}),
            'jumlah': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_jumlah'}),
            'harga_satuan': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_harga_satuan'}),
            'kondisi': forms.Select(attrs={'class': 'd-none'}),
            'lokasi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Ruang TU'}),
            'pengguna': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama pemegang saat ini'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Catatan tambahan (opsional)'}),
            }

    def clean_kode_barang(self):
        kode_barang = self.cleaned_data['kode_barang']
        queryset = Asset.objects.filter(kode_barang=kode_barang)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError('Kode barang ini sudah digunakan. Silakan gunakan kode lain.')
        return kode_barang