from django import forms
from .models import BarangATK, StokUnit


class BarangATKForm(forms.ModelForm):
    class Meta:
        model = BarangATK
        fields = ['kategori', 'kode_barang', 'nama_barang', 'satuan', 'stok', 'keterangan']
        widgets = {
            'kategori': forms.Select(attrs={'class': 'd-none'}),
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

class StokUnitForm(forms.ModelForm):
    class Meta:
        model = StokUnit
        fields = ['kategori', 'kode_barang', 'nama_barang', 'satuan', 'stok', 'keterangan']
        widgets = {
            'kategori': forms.Select(attrs={'class': 'd-none'}),
            'kode_barang': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ATK-001'}),
            'nama_barang': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Kertas A4'}),
            'satuan': forms.Select(attrs={'class': 'd-none'}),
            'stok': forms.NumberInput(attrs={'class': 'form-control'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Catatan tambahan (opsional)'}),
        }
    
        def clean(self):
            cleaned = super().clean()
            kode = cleaned.get('kode_barang')
            nama = (cleaned.get('nama_barang') or '').strip().lower()
            if kode:
                barang_pusat = BarangATK.objects.filter(kode_barang=kode).first()
                if barang_pusat and barang_pusat.nama_barang.strip().lower() != nama:
                    self.add_error(
                        'kode_barang',
                        f'Kode ini dipakai barang Dinas "{barang_pusat.nama_barang}". Gunakan kode lain.'
                    )
            return cleaned