from django import forms
from .models import BarangATK


class BarangATKForm(forms.ModelForm):
    class Meta:
        model = BarangATK
        fields = ['kode_barang', 'nama_barang', 'satuan', 'stok', 'keterangan']
        widgets = {
            'kode_barang': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ATK-001'}),
            'nama_barang': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Kertas A4'}),
            'satuan': forms.Select(attrs={'class': 'd-none'}),
            'stok': forms.NumberInput(attrs={'class': 'form-control'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Catatan tambahan (opsional)'}),
        }

    def clean_kode_barang(self):
        kode_barang = self.cleaned_data['kode_barang']
        qs = BarangATK.objects.filter(kode_barang=kode_barang)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Kode barang ini sudah digunakan.')
        return kode_barang