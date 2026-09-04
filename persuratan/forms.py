from django import forms
from .models import SuratMasuk, SuratKeluar


class SuratMasukForm(forms.ModelForm):
    class Meta:
        model = SuratMasuk
        fields = [
            'nomor_agenda', 'nomor_surat', 'asal_surat', 'perihal', 'sifat',
            'tanggal_surat', 'tanggal_diterima', 'file_scan',
        ]
        widgets = {
            'nomor_agenda': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 001'}),
            'nomor_surat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor surat dari pengirim'}),
            'asal_surat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Instansi/pihak pengirim'}),
            'perihal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Perihal surat'}),
            'sifat': forms.Select(attrs={'class': 'form-select'}),
            'tanggal_surat': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tanggal_diterima': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'file_scan': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class SuratKeluarForm(forms.ModelForm):
    class Meta:
        model = SuratKeluar
        fields = [
            'nomor_agenda', 'nomor_surat', 'tujuan_surat', 'perihal', 'sifat',
            'tanggal_surat', 'file_scan',
        ]
        widgets = {
            'nomor_agenda': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 001'}),
            'nomor_surat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 005/DPPKB/IX/2026'}),
            'tujuan_surat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Instansi/pihak tujuan'}),
            'perihal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Perihal surat'}),
            'sifat': forms.Select(attrs={'class': 'form-select'}),
            'tanggal_surat': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'file_scan': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }