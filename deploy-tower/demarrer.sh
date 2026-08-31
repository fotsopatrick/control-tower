#!/usr/bin/env bash
# One script. It brings up the database, waits until it is really ready,
# creates the tower's database the first time, installs the missing package,
# and leaves Odoo serving. Idempotent: run it again, it just restarts.
#
#   ./demarrer.sh
#
# Requires: docker, and the modules in ./custom-addons (see README).
set -euo pipefail
cd "$(dirname "$0")"

# --- passwords, generated once, never committed ------------------------------
if [ ! -f .env ]; then
  printf 'POSTGRES_PASSWORD=%s\nODOO_ADMIN_PASSWD=%s\n' \
    "$(openssl rand -base64 18 | tr -d '/+=' | head -c 18)" \
    "$(openssl rand -base64 18 | tr -d '/+=' | head -c 18)" > .env
  chmod 600 .env
  echo "[demarrer] .env created"
fi
P=$(grep POSTGRES_PASSWORD .env | cut -d= -f2)

# --- odoo.conf, if the compose mounts one ------------------------------------
if [ ! -f odoo.conf ]; then
  cat > odoo.conf <<CONF
[options]
addons_path = /mnt/extra-addons
data_dir = /var/lib/odoo
list_db = True
dbfilter = ^tour_prod$
CONF
fi

echo "[demarrer] starting containers..."
sudo docker compose up -d

echo "[demarrer] waiting for postgres to accept connections..."
for i in $(seq 1 60); do
  if sudo docker compose exec -T db pg_isready -U odoo >/dev/null 2>&1; then
    echo "[demarrer] postgres ready after ${i}s"; break
  fi
  sleep 1
done

# --- create the database the first time only ---------------------------------
HAS_DB=$(sudo docker compose exec -T db psql -U odoo -d postgres -t -A \
  -c "SELECT 1 FROM pg_database WHERE datname='tour_prod';" 2>/dev/null | tr -d '[:space:]')
if [ "$HAS_DB" != "1" ]; then
  echo "[demarrer] first run: creating tour_prod (2-4 min)..."
  sudo docker compose run --rm --entrypoint odoo tour \
    -d tour_prod -i base,web,tour_community_chat,tour_community_braignak \
    --db_host=db --db_user=odoo --db_password="$P" --stop-after-init
else
  echo "[demarrer] tour_prod already exists, skipping creation"
fi

# --- the package the published image is missing ------------------------------
sudo docker compose exec -T tour python3 -c "import qifparse" 2>/dev/null || {
  echo "[demarrer] installing qifparse..."
  sudo docker compose exec -T tour pip install --break-system-packages -q qifparse || true
}

echo "[demarrer] restarting odoo to serve cleanly..."
sudo docker compose restart tour
sleep 15

echo "[demarrer] done. Open http://<this-machine-ip>:8069  (admin / see .env)"
sudo docker compose ps --format "  {{.Service}} {{.Status}}"
