"""Turn goatcounter.json into one flat table (rows.json) for the stats dashboard."""
import json, sys
d = json.load(open(sys.argv[1]))
rows = []
def add(kind, key, label, value, group=""):
    rows.append({"kind": kind, "key": str(key), "label": label, "value": int(value or 0), "group": group})

hits = [h for h in (d.get("hits") or {}).get("hits") or [] if not h.get("event")]
days = {}
for h in hits:
    for s in h.get("stats") or []:
        days[s["day"]] = days.get(s["day"], 0) + (s.get("daily") or 0)
first = min((k for k, v in days.items() if v), default=None)
for day in sorted(days):
    if first and day >= first:
        add("daily", day, day, days[day])
for h in hits:
    p = h.get("path", "")
    title = (h.get("title") or p).split(" · ")[0]
    group = "Trap-pagina" if p.startswith("/traps/") else ("Fout (404)" if "404" in p else "Overige pagina")
    add("page", p, title, h.get("count"), group)
for r in (d.get("toprefs") or {}).get("stats") or []:
    name = r.get("name") or ""
    label = name or "Direct of onbekend"
    group = "Direct" if not name else ("Video" if "youtube" in name else ("Zoekmachine" if any(x in name for x in ("google", "bing", "duckduckgo", "ecosia", "yahoo")) else ("Social" if any(x in name for x in ("instagram", "tiktok", "facebook", "t.co", "reddit")) else ("Bot of scanner" if "urlscan" in name else "Website"))))
    add("source", name or "(direct)", label, r.get("count"), group)
for r in (d.get("locations") or {}).get("stats") or []:
    add("country", r.get("id"), r.get("name") or r.get("id"), r.get("count"))
names = {"phone": "Telefoon", "tablet": "Tablet", "desktop": "Computer", "desktophd": "Computer (groot scherm)", "unknown": "Onbekend"}
for r in (d.get("sizes") or {}).get("stats") or []:
    if r.get("count"):
        add("device", r.get("id"), names.get(r.get("id"), r.get("id")), r.get("count"))
for kind, page in (("browser", "browsers"), ("system", "systems")):
    for r in (d.get(page) or {}).get("stats") or []:
        add(kind, r.get("id") or r.get("name"), r.get("name") or r.get("id"), r.get("count"))
for r in (d.get("campaigns") or {}).get("stats") or []:
    add("campaign", r.get("id") or r.get("name"), r.get("name") or r.get("id"), r.get("count"))
json.dump({"generated": d.get("generated"), "start": d.get("start"), "end": d.get("end"), "rows": rows}, open(sys.argv[2], "w"), ensure_ascii=False, indent=0)
print(len(rows), "rows")
