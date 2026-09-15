# SIPANDU-KB

**Sistem Informasi Pelayanan dan Data Terpadu** — DPPKB Kota Samarinda

Aplikasi web berbasis Django untuk manajemen aset, persuratan, dan permintaan ATK di lingkungan DPPKB Kota Samarinda.

## Fitur Utama

- **Manajemen Aset** — pencatatan aset, pengajuan service/pemeliharaan, pindah tangan aset (dengan cetak Berita Acara Serah Terima ber-kop-surat), notifikasi pajak & ganti oli kendaraan
- **Persuratan** — surat masuk & surat keluar, lembar disposisi digital (dengan cetak PDF)
- **Permintaan ATK** — permintaan barang antar unit kerja, riwayat kebutuhan ATK tahunan
- **Manajemen Pengguna** — role & hak akses (Admin, Manager, Operator, Kasubag Umum, Tamu)
- **Permintaan Data** — akses khusus untuk pihak luar (mahasiswa/OPD lain) mengajukan permintaan data

## Teknologi

- **Backend:** Django 4.2
- **Database:** MySQL
- **PDF Generation:** ReportLab
- **Frontend:** Bootstrap 5

## Prasyarat

Sebelum instalasi, pastikan sudah terpasang:

- Python 3.10 atau lebih baru
- MySQL Server (XAMPP/Laragon/MySQL native)
- Git

## Panduan Instalasi

### 1. Clone Repository

```bash
git clone <url-repository-ini>
cd "Website - Sipandu"
```

### 2. Buat Virtual Environment

```bash
python -m venv venv
```

Aktifkan virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Siapkan Database

Buat database MySQL baru:

```sql
CREATE DATABASE sipandu;
```

Sesuaikan konfigurasi koneksi database di `sipandu/settings.py` jika perlu (default menggunakan user `root` tanpa password, host `localhost`):

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sipandu',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

### 5. Jalankan Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Buat Superuser (Akun Admin)

```bash
python manage.py createsuperuser
```

Ikuti instruksi untuk membuat username, email, dan password.

### 7. Jalankan Server

```bash
python manage.py runserver
```

Buka browser dan akses:

```
http://127.0.0.1:8000
```

Login menggunakan akun superuser yang sudah dibuat, atau buat akun pengguna baru dengan role tertentu (Admin/Manager/Operator/Kasubag Umum/Tamu) lewat menu **Pengaturan → Pengguna**.

## Struktur Folder

```
Website - Sipandu/
├── manage.py
├── requirements.txt
├── sipandu/           # Konfigurasi utama proyek Django
├── dashboard/         # Dashboard per role
├── asset/             # Manajemen aset & service kendaraan
├── persuratan/        # Surat masuk/keluar & lembar disposisi
├── databarang/        # Permintaan ATK & riwayat kebutuhan
├── pengguna/           # Manajemen pengguna & profil
├── tamu/               # Permintaan data untuk pihak luar
├── templates/          # Template HTML
├── static/             # File statis (logo, dll)
└── media/               # File hasil upload pengguna (surat scan, dll)
```

## Role & Hak Akses

| Role | Akses |
|---|---|
| **Admin** | Akses penuh ke seluruh modul |
| **Manager** | Dashboard, Aset, Persuratan, ATK, Laporan |
| **Operator** | Dashboard, Aset, Persuratan, ATK (sesuai unit kerja) |
| **Kasubag Umum** | Dashboard, Aset, Approval Service, Persuratan, ATK, Permintaan Data |
| **Tamu** | Permintaan Data (untuk pihak luar/mahasiswa/OPD lain) |

Selain role, setiap pengguna juga punya **jenis akun**: `Umum` (akses lintas unit kerja) atau `Balai`/`Bidang` (akses terbatas pada data unit kerja masing-masing).

## Catatan

- Folder `media/` menyimpan file hasil upload (scan surat, dll) — pastikan folder ini punya izin tulis.
- Untuk keperluan produksi (bukan development), sesuaikan `DEBUG = False` dan konfigurasi keamanan lain di `settings.py`.
