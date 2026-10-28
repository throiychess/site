"""Fetch aggregate GoatCounter stats (no personal data) and write goatcounter.json.
Runs in GitHub Actions; token comes from the GOATCOUNTER_TOKEN secret."""
import json, os, sys, time, urllib.request, urllib.parse, datetime as dt

BASE = "https://throiychess.goatcounter.com/api/v0"
TOKEN = os.environ["GOATCOUNTER_TOKEN"]
today = dt.date.today()
start = (today - dt.timedelta(days=89)).isoformat()
end = today.isoformat()

def get(path, **params):
    q = urllib.parse.urlencode({"start": start, "end": end, **params})
    req = urllib.request.Request(f"{BASE}{path}?{q}", headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                time.sleep(0.35)  # API limit: 4 requests/second
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2); continue
            print(f"{path}: HTTP {e.code} {e.read()[:300]!r}", file=sys.stderr)
            return {"error": e.code}
    return {"error": "rate limited"}

out = {"generated": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z", "start": start, "end": end}
out["total"] = get("/stats/total")
out["hits"] = get("/stats/hits", limit=100, daily="true")
for page in ["toprefs", "browsers", "systems", "sizes", "locations", "campaigns"]:
    out[page] = get(f"/stats/{page}", limit=50)
# referrers for the 10 most viewed pages
refs = {}
for h in (out["hits"].get("hits") or [])[:10]:
    pid = h.get("path_id")
    if pid is not None:
        refs[h.get("path")] = get(f"/stats/hits/{pid}", limit=10)
out["page_refs"] = refs

json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "goatcounter.json", "w"), indent=1)
print("ok", {k: (list(v) if isinstance(v, dict) else v) for k, v in out.items() if k in ("total", "hits")})
