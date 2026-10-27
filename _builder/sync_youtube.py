"""Fetch the ThroiyChess YouTube feed and write youtube.json (id, title, date, desc). Runs in GitHub Actions."""
import json, os, re, http.client, urllib.request, xml.etree.ElementTree as ET
def kind(vid):
    try:
        c = http.client.HTTPSConnection("www.youtube.com", timeout=20)
        c.request("HEAD", f"/shorts/{vid}", headers={"User-Agent": "Mozilla/5.0"}); st = c.getresponse().status
        return "video" if st in (301, 302, 303, 307, 308) else "short" if st == 200 else None
    except Exception: return None
CH = "UCOlTPoaNud_2lNwjNmH9diw"
ns = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015", "m": "http://search.yahoo.com/mrss/"}
xml = None
for attempt in range(3):  # YouTube's feed sometimes fails for a moment; retry, and never fail the job over it
    try:
        xml = urllib.request.urlopen(f"https://www.youtube.com/feeds/videos.xml?channel_id={CH}", timeout=30).read(); break
    except Exception as err:
        print("feed attempt", attempt + 1, "failed:", err); __import__("time").sleep(20)
if xml is None:
    print("feed unavailable, keeping the current list"); raise SystemExit(0)
out = []
for e in ET.fromstring(xml).findall("a:entry", ns):
    title = re.sub(r"\s*[♟️#].*$", "", e.find("a:title", ns).text).strip()
    desc = (e.find("m:group/m:description", ns).text or "").split("\n")[0][:220]
    out.append(dict(id=e.find("yt:videoId", ns).text, title=title, date=e.find("a:published", ns).text[:10], topic="", desc=desc))
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube.json")
old = open(p).read() if os.path.exists(p) else ""
prev = {v["id"]: v.get("kind") for v in (json.loads(old) if old else [])}
for v in out: v["kind"] = prev.get(v["id"]) or kind(v["id"]) or "short"
new = json.dumps(out, ensure_ascii=False, indent=1)
if new != old: open(p, "w").write(new); print("updated", len(out))
else: print("no change")
