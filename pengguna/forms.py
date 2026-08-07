from django import forms
from django.contrib.auth.models import User
from .models import Profile


class PenggunaForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan username'})
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan password'})
    )

    class Meta:
        model = Profile
        fields = ['nama_lengkap', 'jabatan', 'unit_kerja', 'role', 'status']
        widgets = {
            'nama_lengkap': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama lengkap beserta gelar'}),
            'jabatan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Kepala Biro Umum'}),
            'unit_kerja': forms.Select(attrs={'class': 'd-none'}),
            'role': forms.Select(attrs={'class': 'd-none'}),
            'status': forms.Select(attrs={'class': 'd-none'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['username'].initial = self.instance.user.username
            self.fields['password'].help_text = 'Kosongkan jika tidak ingin mengubah password.'
        else:
            self.fields['password'].required = True

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise forms.ValidationError('Username ini sudah digunakan.')
        return username

    def save(self, commit=True):
        profile = super().save(commit=False)

        if profile.pk:
            user = profile.user
        else:
            user = User()

        user.username = self.cleaned_data['username']

        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        elif not user.pk:
            user.set_unusable_password()

        user.is_active = (self.cleaned_data.get('status') == 'aktif')

        user.save()
        profile.user = user

        if commit:
            profile.save()

        return profile