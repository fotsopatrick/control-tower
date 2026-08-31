# Faithful reproduction — restore the live tower from a snapshot

The other recipe (`../deploy-tower/`) builds the tower from scratch. This one
does the opposite: it restores a **snapshot of the running database** and
filestore, so what boots is byte-identical to the deployed tower — 88 modules,
the theme, 22 agents, 25 circuits, the cockpit — in about 30 seconds after the
first restore.

## Why a snapshot, not a fresh install

A fresh install re-runs every module's setup and depends on the published
image being complete. A snapshot skips all of that: the database already *is*
the tower. This is how the judged deployment at `34.155.174.180` was built.

## What you need next to `docker-compose.yml`

Three things are **not** in this public repo (they carry data and API keys):

- `tour.dump` — a `pg_dump -Fc` of the `tour_azure` database
- `custom-addons/` — the 93 modules, from the sibling repo `tour-community`
- `.env` is generated on first run

Get them like this:

```bash
# the modules
git clone https://github.com/fotsopatrick/tour-community.git
cp -r tour-community/custom-addons ./custom-addons

# the snapshot: ask the maintainer, or take one from any running tower:
#   docker compose exec -T db pg_dump -U odoo -d tour_azure -Fc > tour.dump
```

## Run

```bash
docker compose up -d
# first run restores the snapshot, then Odoo serves it
```

Open `http://<ip>:8069` — `admin` / `admin`.

## One gotcha, seen on some hosts

If the tower logs `could not translate host name "db"`, the host's Docker DNS
is broken (not this project). Work around it by pointing `--db_host` at the
db container's IP:

```bash
IP=$(docker inspect $(docker compose ps -q db) \
     --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')
sed -i "s/--db_host=db/--db_host=$IP/" docker-compose.yml
docker compose up -d tour
```

## Tested

Verified twice, end to end: on a fresh Google Compute Engine VM and on a local
Ubuntu machine. All ten pages return 200 (dashboard, apps, cockpit, agents,
defense, circuits, decisions, messages, reponses, odoo); 155 modules loaded,
22 active agents, 25 circuits, theme rendered.
