"""read_carte — answers questions over the living map. No model involved.

The living map is a survey of what actually exists in the tower: services,
containers, volumes, agents, circuits, tools. This circuit reads it and answers
directly, which is the whole point: a question whose answer is already written
down does not need a language model.

    python3 relever-carte-apps.py                 -> summary of every zone
    python3 relever-carte-apps.py <words>         -> search across all entries
    python3 relever-carte-apps.py --zone <name>   -> list one zone
    python3 relever-carte-apps.py --type <kind>   -> group by kind
"""
import json
import pathlib
import sys
import unicodedata

MAP = pathlib.Path(__file__).resolve().parent.parent / "cartes.json"


def fold(text):
    """Lowercase and strip accents, so 'facade' finds 'façade'."""
    t = unicodedata.normalize("NFD", str(text or ""))
    return "".join(c for c in t if unicodedata.category(c) != "Mn").lower()


def load():
    if not MAP.exists():
        print("living map not found: %s" % MAP)
        sys.exit(2)
    data = json.loads(MAP.read_text(encoding="utf-8"))
    zones = data.get("zones")
    if zones is None:
        print("unexpected map shape; top-level keys: %s" % list(data)[:8])
        sys.exit(2)
    return data, zones


def entries(zones):
    for z in zones:
        for n in z.get("noeuds", []):
            yield z.get("nom", "?"), n


def summary(data, zones):
    total = sum(len(z.get("noeuds", [])) for z in zones)
    print("LIVING MAP — surveyed %s" % data.get("releve_le", "unknown date"))
    print("%d entries across %d zones" % (total, len(zones)))
    print()
    for z in sorted(zones, key=lambda z: -len(z.get("noeuds", []))):
        print("  %-22s %4d" % (z.get("nom", "?"), len(z.get("noeuds", []))))
    kinds = {}
    for _, n in entries(zones):
        kinds[n.get("type", "?")] = kinds.get(n.get("type", "?"), 0) + 1
    print()
    print("  by kind:")
    for k, v in sorted(kinds.items(), key=lambda kv: -kv[1])[:8]:
        print("    %-20s %4d" % (k, v))


def search(zones, words):
    needle = fold(" ".join(words))
    hits = []
    for zone, n in entries(zones):
        hay = fold("%s %s %s" % (n.get("nom"), n.get("type"), n.get("detail")))
        if needle in hay:
            hits.append((zone, n))
    print("%d entr%s matching %r" % (len(hits), "y" if len(hits) == 1 else "ies",
                                     " ".join(words)))
    for zone, n in hits[:40]:
        detail = str(n.get("detail") or "").replace("\n", " ")[:88]
        print("  [%s] %s — %s" % (zone, n.get("nom"), detail))
    if len(hits) > 40:
        print("  ... and %d more (not shown)" % (len(hits) - 40))
    if not hits:
        print("  Absent from the map. That is not the same as 'does not exist'.")
    return len(hits)


def one_zone(zones, name):
    want = fold(name)
    for z in zones:
        if want in fold(z.get("nom")):
            ns = z.get("noeuds", [])
            print("%s — %d entries" % (z.get("nom"), len(ns)))
            for n in ns:
                print("  %-34s %-14s %s" % (str(n.get("nom"))[:34],
                                            str(n.get("type"))[:14],
                                            str(n.get("detail") or "")[:60]))
            return
    print("No zone matching %r. Zones: %s"
          % (name, ", ".join(z.get("nom", "?") for z in zones)))


def main():
    data, zones = load()
    args = sys.argv[1:]
    if not args:
        summary(data, zones)
    elif args[0] == "--zone" and len(args) > 1:
        one_zone(zones, " ".join(args[1:]))
    elif args[0] == "--type" and len(args) > 1:
        search(zones, args[1:])
    else:
        search(zones, args)


if __name__ == "__main__":
    main()
