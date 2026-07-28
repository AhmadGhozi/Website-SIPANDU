from django import forms
from .models import Asset


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['kode_barang', 'nama_barang', 'merk_type', 'jumlah', 'harga_satuan']
        widgets = {
            'kode_barang': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AST-009'}),
            'nama_barang': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama asset'}),
            'merk_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Dell / Latitude 5520'}),
            'jumlah': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_jumlah'}),
            'harga_satuan': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_harga_satuan'}),
        }

    def clean_kode_barang(self):
        kode_barang = self.cleaned_data['kode_barang']
        queryset = Asset.objects.filter(kode_barang=kode_barang)

        # Saat mode edit, kecualikan data milik asset itu sendiri dari pengecekan
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError('Kode barang ini sudah digunakan. Silakan gunakan kode lain.')

        return kode_barang