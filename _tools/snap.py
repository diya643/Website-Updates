"""Screenshot a page from the local preview server.
usage: python3 _tools/snap.py /path [width] [selector] [out-name]
Writes _tools/shots/<name>.png (full page, or just the selector's element)."""
import sys, re
from pathlib import Path
from playwright.sync_api import sync_playwright
path = sys.argv[1]; w = int(sys.argv[2]) if len(sys.argv) > 2 else 1440
sel = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "-" else None
name = sys.argv[4] if len(sys.argv) > 4 else (re.sub(r"\W+", "-", path.strip("/")) or "home") + f"-{w}" + ("-" + re.sub(r"\W+", "", sel) if sel else "")
out = Path(__file__).parent / "shots"; out.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": w, "height": 900}, device_scale_factor=1)
    pg.goto("http://localhost:4610" + path, wait_until="networkidle")
    pg.wait_for_timeout(700)
    pg.add_style_tag(content=".reveal{opacity:1!important;transform:none!important} .ucp-scene.on .ucp-in{animation:none!important;opacity:1!important} .ucp-scene.on .ucp-type{animation:none!important;clip-path:none!important} .ucp-scene.on .ucp-bar::after{animation:none!important;width:var(--w,100%)!important} .ucp-scene.on .ucp-tick .s{display:none} .ucp-scene.on .ucp-tick .c{animation:none!important;opacity:1!important}")
    f = out / f"{name}.png"
    if sel:
        pg.locator(sel).first.screenshot(path=str(f))
    else:
        pg.screenshot(path=str(f), full_page=True)
    b.close()
print(f)
