# Deployment & Automation Nextcloud 34 (Docker)

Repositori ini berisi konfigurasi dan skrip otomasi untuk melakukan deployment lingkungan Nextcloud 34 berbasis Docker, meliputi:
- Pemasangan modul Team Folders (groupfolders v22.0.6) secara otomatis.
- Pembuatan akun pengguna, grup divisi, dan struktur Team Folders.
- Pengunggahan berkas uji via WebDAV serta konfigurasi skenario sharing (ACL).

---

## Prasyarat Sistem

- Docker & Docker Compose
- Python 3.x + library requests (pip install requests)
- Git

---

## Struktur Repositori

.
├── docker-compose.yml     # Konfigurasi container Nextcloud & PostgreSQL
├── seed_files.py          # Skrip Python pengunggah berkas via WebDAV & OCS Share
├── seed/
│   ├── manifest.csv       # Daftar manifest 23 berkas uji
│   ├── seed_server.sh     # Skrip bash otomatisasi user, group, & groupfolders
│   └── docs/              # Direktori berkas dokumen uji
├── .gitignore             # Mengabaikan berkas rahasia (.env) dari repositori
└── README.md

---

## Alur Pemasangan & Eksekusi (Quick Start)

### 1. Buat Berkas Konfigurasi Lingkungan (.env)

Buat berkas .env dan seed/accounts.env di mesin lokal:

# Konfigurasi Database & Admin Nextcloud
cat << "ENV" > .env
DB_PASSWORD=SecurePassDB-2026!
ADMIN_PASSWORD=SecurePassAdmin-2026!
ENV

# Konfigurasi Password Akun Pengguna
cat << "ENV" > seed/accounts.env
PW_budi=Pass-Budi-2026!
PW_sari=Pass-Sari-2026!
PW_maya=Pass-Maya-2026!
PW_andi=Pass-Andi-2026!
PW_dodi=Pass-Dodi-2026!
PW_rina=Pass-Rina-2026!
PW_eko=Pass-Eko-2026!
ENV

### 2. Jalankan Container Docker

docker compose up -d

### 3. Inisialisasi Server & Team Folders

docker compose exec -u www-data app bash /seed/seed_server.sh

### 4. Unggah Berkas & Konfigurasi Skenario Sharing (ACL)

python3 seed_files.py

---

## Verifikasi Deployment

1. Cek Status Modul Groupfolders:
   docker compose exec -u www-data app php occ app:list | grep groupfolders

2. Cek Daftar Team Folders:
   docker compose exec -u www-data app php occ groupfolders:list

3. Akses Web UI:
   Akses http://localhost:8080 di browser.
