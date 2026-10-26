"""Fetch the ThroiyChess YouTube feed and write youtube.json (id, title, date, desc). Runs in GitHub Actions."""
import json, os, re, urllib.request, xml.etree.ElementTree as ET
CH = "UCOlTPoaNud_2lNwjNmH9diw"
ns = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015", "m": "http://search.yahoo.com/mrss/"}
xml = urllib.request.urlopen(f"https://www.youtube.com/feeds/videos.xml?channel_id={CH}", timeout=30).read()
out = []
for e in ET.fromstring(xml).findall("a:entry", ns):
    title = re.sub(r"\s*[♟️#].*$", "", e.find("a:title", ns).text).strip()
    desc = (e.find("m:group/m:description", ns).text or "").split("\n")[0][:220]
    out.append(dict(id=e.find("yt:videoId", ns).text, title=title, date=e.find("a:published", ns).text[:10], topic="", desc=desc))
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube.json")
old = open(p).read() if os.path.exists(p) else ""
new = json.dumps(out, ensure_ascii=False, indent=1)
if new != old: open(p, "w").write(new); print("updated", len(out))
else: print("no change")
