# Deploying the open-source tower on a fresh machine

This reproduces the second deployment: the tower itself — 93 in-house Odoo
modules, 21 circuit templates, 67 control gates, 58 skills, 22 agents.

**Live:** http://34.155.174.180:8069 — `admin` / `admin`

The judged control plane runs separately on Cloud Run and needs no
credentials. This tower is the platform it governs.

## Two repositories, one deployment

The compose file lives here, in **control-tower**. The 93 Odoo modules live in
the sister repository **tour-community**. You need both, side by side. This is
deliberate: the modules are a separate open-source project, disclosed as
pre-existing work.

## Copy-paste, on a clean Ubuntu 22.04 machine

```bash
# 1. Docker
sudo apt-get update -qq
sudo apt-get install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt-get update -qq
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 2. Both repositories, side by side
git clone https://github.com/fotsopatrick/control-tower.git
git clone https://github.com/fotsopatrick/tour-community.git
cd control-tower/deploy-tower

# 3. Bring the 93 modules next to the compose file
cp -r ../../tour-community/custom-addons ./custom-addons

# 4. The Odoo config the compose file mounts
cat > odoo.conf <<'CONF'
[options]
addons_path = /mnt/extra-addons
data_dir = /var/lib/odoo
list_db = True
dbfilter = ^tour_prod$
CONF

# 5. Passwords, generated here, never committed
printf 'POSTGRES_PASSWORD=%s\nODOO_ADMIN_PASSWD=%s\n' \
  "$(openssl rand -base64 18 | tr -d '/+=' | head -c 18)" \
  "$(openssl rand -base64 18 | tr -d '/+=' | head -c 18)" > .env
chmod 600 .env

# 6. Start
sudo docker compose up -d

# 7. Create the database with a first module (2-4 min).
#    Wait ~15s after step 6 so Postgres is ready before this runs.
sleep 15
P=$(grep POSTGRES_PASSWORD .env | cut -d= -f2)
sudo docker compose run --rm --entrypoint odoo tour -d tour_prod \
  -i base,web,tour_community_chat \
  --db_host=db --db_user=odoo --db_password="$P" --stop-after-init

# 8. The extra Python package the image is missing
sudo docker compose exec -T tour pip install --break-system-packages qifparse
sudo docker compose restart tour
```

Open `http://<machine-ip>:8069`, sign in with `admin` and your generated admin
password. From the home page, click **Apps** (top-left grid) for the tower's
own launcher.

## The traps, written down because they cost an evening

**1. Safety that bites its own tail.** The image sets `list_db = False`, so
Odoo cannot resolve *which* database to open and falls back to the selector.
Fix: name the database on the command line (`--database`) or via `dbfilter`,
with `list_db = True`.

**2. One missing package breaks every page.** Without `qifparse`, every request
returns 500. Step 8 installs it. To bake it in permanently, add it to the
image (`requirements-extra.txt`).

**3. Some modules ship without their `models` folder** in the image published
on ghcr — the publish workflow last failed on 29 August. Mounting the modules
from the tour-community checkout (step 3) sidesteps the stale image entirely.

## Honest limits

Plain HTTP, a demo `admin`/`admin` account, no personal data — a test database.
Do not put anything real behind an unencrypted login.
