from django import forms
from .models import PermintaanData


class PermintaanDataForm(forms.ModelForm):
    class Meta:
        model = PermintaanData
        fields = ['nama_pemohon', 'asal_instansi', 'keperluan', 'data_diminta']
        widgets = {
            'nama_pemohon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama lengkap kamu'}),
            'asal_instansi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Universitas Mulawarman / Dinas Kominfo'}),
            'keperluan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Penelitian Skripsi / Kebutuhan Dinas'}),
            'data_diminta': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Jelaskan data apa saja yang dibutuhkan'}),
        }


class TanggapanPermintaanForm(forms.ModelForm):
    class Meta:
        model = PermintaanData
        fields = ['status', 'catatan_tanggapan']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'catatan_tanggapan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Catatan untuk pemohon (opsional)'}),
        }