import csv
import pathlib
import requests
from urllib.parse import quote

BASE = "http://localhost:8080"
ROOT = pathlib.Path(__file__).parent
SEED = ROOT / "seed"
PW = {}

for line in open(SEED / "accounts.env", encoding="utf-8"):
    if line.strip() and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        PW[k.removeprefix("PW_")] = v

def dav(user, path=""):
    return f"{BASE}/remote.php/dav/files/{user}/{quote(path)}"

def mkdirs(user, path):
    parts = path.split("/")[:-1]
    for i in range(1, len(parts) + 1):
        subpath = "/".join(parts[:i])
        r = requests.request("MKCOL", dav(user, subpath), auth=(user, PW[user]))
        # 201 = Created, 405/409/500 pada folder root (seperti HR/Marketing) dilewati jika sudah ada
        if r.status_code not in (201, 405, 409):
            if i == 1 and r.status_code == 500:
                continue
            r.raise_for_status()

def upload(user, path, content):
    mkdirs(user, path)
    r = requests.put(dav(user, path), data=content, auth=(user, PW[user]))
    r.raise_for_status()

def share(user, path, share_type, share_with=None):
    data = {"path": "/" + path, "shareType": share_type, "permissions": 1}
    if share_with:
        data["shareWith"] = share_with
    r = requests.post(
        f"{BASE}/ocs/v2.php/apps/files_sharing/api/v1/shares",
        data=data,
        params={"format": "json"},
        headers={"OCS-APIRequest": "true"},
        auth=(user, PW[user])
    )
    r.raise_for_status()
    return r.json()["ocs"]["data"]

with open(SEED / "manifest.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
    for row in rows:
        local = SEED / "docs" / row["file_lokal"]
        if local.exists():
            content = local.read_bytes()
        else:
            content = f"{pathlib.Path(row['path']).stem}\n\n(isi dokumen menyusul)\n".encode("utf-8")
        upload(row["pemilik"], row["path"], content)
        print(f"unggah {row['pemilik']:<5} {row['path']}")

SHARES = [
    ("budi", "HR/Gaji 2026", 1, "Semua", "K1 salah share ke grup Semua"),
    ("sari", "Kerjaan Sari/Evaluasi Kinerja Q3.txt", 3, None, "K2 link publik"),
    ("maya", "Marketing/Kampanye Q4", 0, "dodi", "K5 akses proyek tidak dicabut"),
]

for user, path, st, to, kode in SHARES:
    d = share(user, path, st, to)
    print(f"{kode:<32} -> {d.get('url') or d.get('share_with')}")

print(f"SELESAI: {len(rows)} file, {len(SHARES)} share")
