#!/bin/bash
set -e
cd /var/www/html
source /seed/accounts.env

# 1. Pemasangan Groupfolders Kompatibel (v20.0.0)
if [ ! -d /var/www/html/apps/groupfolders ]; then
  echo "Mengunduh modul groupfolders v20.0.0..."
  rm -f /tmp/groupfolders.tar.gz
  curl -L -o /tmp/groupfolders.tar.gz https://github.com/nextcloud-releases/groupfolders/releases/download/v20.0.0/groupfolders-v20.0.0.tar.gz
  tar -xzf /tmp/groupfolders.tar.gz -C /var/www/html/apps/
  chown -R www-data:www-data /var/www/html/apps/groupfolders
fi

php occ app:enable groupfolders || true

# 2. Buat Grup
for g in HR Marketing Finance Semua; do
  php occ group:add "$g" || echo "grup $g sudah ada, dilewati"
done

# 3. Buat Akun Karyawan
add() {
  local u="$1" name="$2"; shift 2
  local pw_var="PW_$u"
  if php occ user:info "$u" > /dev/null 2>&1; then
    echo "akun $u sudah ada, dilewati"
  else
    OC_PASS="${!pw_var}" php occ user:add --password-from-env --display-name="$name" "$u"
    for g in "$@" Semua; do php occ group:adduser "$g" "$u" || true; done
  fi
}

add budi "Budi Santoso" HR
add sari "Sari Wulandari" HR
add maya "Maya Putri" Marketing
add andi "Andi Pratama" Finance Marketing
add dodi "Dodi Hidayat" Finance
add rina "Rina Lestari" Marketing
add eko "Eko Saputra" Marketing

# 4. Buat Team Folders
if php occ groupfolders:list | grep -q "Pengumuman"; then
  echo "Team folders sudah ada, dilewati."
else
  HR=$(php occ groupfolders:create HR)
  MKT=$(php occ groupfolders:create Marketing)
  FIN=$(php occ groupfolders:create Finance)
  PENG=$(php occ groupfolders:create Pengumuman)

  php occ groupfolders:group "$HR" HR write share delete
  php occ groupfolders:group "$MKT" Marketing write share delete
  php occ groupfolders:group "$FIN" Finance write share delete
  php occ groupfolders:group "$PENG" Semua read
  php occ groupfolders:group "$PENG" HR write share delete
fi

php occ groupfolders:list
echo "SELESAI: lanjut jalankan python seed_files.py di komputer host"
