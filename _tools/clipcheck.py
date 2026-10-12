"""Report horizontal overflow on every built page at the given widths.
usage: python3 _tools/clipcheck.py 375 1100 1440"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
pub = Path(__file__).resolve().parent.parent / "public"
paths = sorted("/" + str(p.parent.relative_to(pub)) for p in pub.rglob("index.html"))
widths = [int(x) for x in sys.argv[1:]] or [375, 1280]
JS = """() => { const W = document.documentElement.clientWidth, bad = [];
 document.querySelectorAll('main *').forEach(e => { const r = e.getBoundingClientRect();
  if (r.width && (r.right > W + 1 || r.left < -1)) { let p = e.parentElement, clipped = false;
   while (p && p !== document.body) { const s = getComputedStyle(p); if (/(hidden|auto|scroll|clip)/.test(s.overflowX)) { clipped = true; break } p = p.parentElement }
   if (!clipped) bad.push((e.className && e.className.baseVal === undefined ? e.className : e.tagName) + ' ' + Math.round(r.right - W)) } });
 return {scroll: document.documentElement.scrollWidth - W, bad: bad.slice(0, 5)} }"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in widths:
        pg = b.new_page(viewport={"width": w, "height": 900})
        for path in paths:
            pg.goto("http://localhost:4610" + path, wait_until="load")
            r = pg.evaluate(JS)
            if r["scroll"] > 0 or r["bad"]:
                print(w, path, r)
        pg.close()
    b.close()
print("clipcheck done")
