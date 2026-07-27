from django import forms
from .models import Asset


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['kode_barang', 'nama_barang', 'merk_type', 'jumlah', 'harga_satuan']
        widgets = {
            'kode_barang': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AST-009'}),
            'nama_barang': forms.TextInput(attrs={'class': 'form-control'}),
            'merk_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dell / Latitude 5520'}),
            'jumlah': forms.NumberInput(attrs={'class': 'form-control'}),
            'harga_satuan': forms.NumberInput(attrs={'class': 'form-control'}),
        }