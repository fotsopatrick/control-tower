# Deploying the open-source tower on Google Cloud

This folder reproduces the second deployment of this submission: the tower
itself — 88 in-house Odoo modules, 21 circuit templates, 67 control gates,
58 skills, 22 agents — running on a Google Compute Engine VM.

**Live:** http://34.155.174.180:8069 — `admin` / `admin`

The control plane (the judged part of this submission) runs separately on
Cloud Run and needs no credentials. This tower is the platform it governs.

## Steps

```bash
# 1. A machine. e2-standard-2 is enough: 2 vCPU, 8 GB, ~25 EUR/month.
gcloud compute instances create tour-opensource \
  --zone=europe-west9-b --machine-type=e2-standard-2 \
  --image-family=ubuntu-2204-lts --image-project=ubuntu-os-cloud \
  --boot-disk-size=40GB --tags=tour-web

gcloud compute firewall-rules create autoriser-tour-web \
  --allow=tcp:80,tcp:443,tcp:8069 --target-tags=tour-web

# 2. Docker, then passwords generated ON the machine and never committed.
sudo mkdir -p /opt/tour && cd /opt/tour
printf 'POSTGRES_PASSWORD=%s\nODOO_ADMIN_PASSWD=%s\n' \
  "$(openssl rand -base64 24 | tr -d '/+=' | head -c 24)" \
  "$(openssl rand -base64 24 | tr -d '/+=' | head -c 24)" | sudo tee .env
sudo chmod 600 .env

# 3. This compose file, the addons, and the config. Then:
sudo docker compose up -d

# 4. The extra package the image is missing.
sudo docker compose exec -T tour pip install --break-system-packages qifparse
sudo docker compose restart tour
```

## The two traps, written down because they cost an evening

### 1. Safety that bites its own tail

The published image sets `list_db = False` so nobody can enumerate the
databases. Sensible. But Odoo answers *"which database do I open?"* by reading
that same list. With the list disabled it finds nothing, gives up, and shows
the database selector — the exact screen the setting was meant to avoid.

**Fix:** name the database on the command line — `--database=tour_azure`
together with `--no-database-list`. Setting `dbfilter` alone is not enough.

### 2. One missing Python package breaks every page

Without `qifparse`, every request returns 500 with
`ModuleNotFoundError: No module named 'qifparse'`. One of the accounting
modules imports it. It is listed in `requirements-extra.txt`.

### 3. Known: some modules ship without their `models` folder

In the image published on ghcr, 15 of 20 modules declare
`from . import models` but the folder is absent — the publish workflow last
failed on 29 August, so the registry still serves a build from before those
files were added. Installing them raises what looks like a circular import but
is really a missing file.

**Workaround used here:** mount the addons from a known-good checkout instead
of relying on the image's copy. The compose file above does exactly that with
`./custom-addons:/mnt/extra-addons:ro`.

## Honest limits

This deployment runs over plain HTTP with a demo account. It carries **no
personal data** — it is a copy of a test database. Do not put anything real
behind an unencrypted login.
