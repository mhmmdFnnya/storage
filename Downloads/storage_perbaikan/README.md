# Storage Server Uji — Need-to-Know Guard

Nextcloud 34 + PostgreSQL 16 (Docker Compose) sebagai storage server uji untuk riset Need-to-Know Guard.
Berisi 7 akun karyawan fiktif, 4 grup, 4 Team folders, folder pribadi tiap karyawan (sumber histori kerja),
23 dokumen fiktif, dan 7 kasus ACL yang sengaja ditanam (K1–K7).

> Lingkup repo ini: **arsitektur storage saja**. Integrasi AI (konektor + guard) menyusul.

## Isi repo

```
storage/
├─ docker-compose.yml        # Nextcloud 34 + PostgreSQL 16
├─ .env.example              # salin jadi .env
├─ seed/
│  ├─ seed_server.sh         # grup, akun, Team folders, K4
│  ├─ accounts.env.example   # salin jadi seed/accounts.env
│  ├─ manifest.csv           # daftar 23 file + kunci jawaban (perlu_tahu)
│  └─ docs/                  # isi dokumen fiktif
└─ seed_files.py             # unggah file + share K1, K2, K5
```

## Prasyarat

- Docker Engine + Docker Compose
- Python 3 + `requests` (`pip install requests` atau `sudo apt install -y python3-requests`)
- `cloudflared` (hanya kalau server perlu diakses dari luar, mis. Google Colab)

## Langkah 1 · Siapkan file rahasia

```bash
git clone https://github.com/mhmmdFnnya/storage.git
cd storage
cp .env.example .env                              # ganti passwordnya
cp seed/accounts.env.example seed/accounts.env
```

`.env` dan `seed/accounts.env` tidak ikut ter-commit (sudah ada di `.gitignore`).

## Langkah 2 · Nyalakan server

```bash
docker compose up -d
docker compose logs -f app       # tunggu sampai instalasi selesai, lalu Ctrl+C
docker compose exec -u www-data app php occ status    # harus: installed: true
```

Kalau sebelumnya pernah menyalakan server dengan `.env` yang salah, mulai bersih dulu:
`docker compose down -v` (semua data server terhapus), lalu ulangi Langkah 2.

## Langkah 3 · Buat grup, akun, dan Team folders

```bash
docker compose exec -u www-data app bash /seed/seed_server.sh
```

Di akhir muncul tabel `groupfolders:list` berisi 4 folder: HR, Marketing, Finance, Pengumuman.
Tidak perlu membuat grup atau folder manual: semua sudah ada di skrip.

## Langkah 4 · Unggah dokumen dan tanam kasus share

```bash
python3 seed_files.py
```

Output terakhir harus `SELESAI: 23 file, 3 share`. Jalankan **sekali** saja (diulang = share ganda).

## Langkah 5 · Cek hasil

Login di `http://localhost:8080` sebagai akun berikut (pakai jendela incognito) dan cocokkan:

| Login | Harus terlihat | Tidak boleh terlihat | Kasus |
|---|---|---|---|
| `maya` | `/Marketing`, `/Pengumuman`, folder `Gaji 2026` (dibagikan) | isi `/HR` lainnya, `/Finance` | K1 |
| `rina` | `/Marketing`, `/Pengumuman` termasuk `Rencana PHK 2026`; tidak ada folder pribadi | `/HR`, `/Finance` | K3, K6 |
| `andi` | `/Finance` **dan** `/Marketing`, folder `Kerjaan Andi` | `/HR` | K4 |
| `dodi` | `/Finance`, folder `Kampanye Q4` (dibagikan) | `/HR`, isi `/Marketing` lainnya | K5 |
| `eko` | `/Marketing` | `/HR`, `/Finance` | K7 |
| tanpa login | link publik (dari output Langkah 4) membuka `Evaluasi Kinerja Q3` | | K2 |

## Kasus ACL yang ditanam

| Kode | Kasus nyata | Cara ditanam |
|---|---|---|
| K1 | salah share ke grup terlalu luas | `budi` membagikan `/HR/Gaji 2026` ke grup **Semua** |
| K2 | "anyone with the link" | `sari` membuat link publik `Evaluasi Kinerja Q3` |
| K3 | file salah taruh | `Rencana PHK 2026` diunggah ke `/Pengumuman` |
| K4 | pindah divisi, akses lama tidak dicabut | `andi` masih anggota grup Marketing |
| K5 | akses sementara tidak dicabut | `maya` membagikan `/Marketing/Kampanye Q4` ke `dodi` |
| K6 | karyawan baru | `rina` tanpa file pribadi (histori kosong) |
| K7 | mantan karyawan, akun masih aktif | `eko` masih aktif di grup Marketing |

Kunci jawaban (siapa yang sebenarnya perlu tahu setiap file) ada di kolom `perlu_tahu` pada `seed/manifest.csv`.

## (Opsional) Akses dari luar lewat Cloudflare Tunnel

```bash
cloudflared tunnel --url http://localhost:8080        # biarkan terminal ini terbuka
docker compose exec -u www-data app php occ config:system:set trusted_domains 2 --value=<acak>.trycloudflare.com
```

Alamat tunnel berganti setiap dijalankan dan bisa dibuka siapa saja yang tahu alamatnya: matikan setelah selesai.

## Perintah sehari-hari

| Mau apa | Perintah |
|---|---|
| Matikan sementara | `docker compose stop` |
| Nyalakan lagi | `docker compose start` |
| Hapus semua dan mulai dari nol | `docker compose down -v` |
