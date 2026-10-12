"""Capture every scene of every use-case player on a page.
usage: python3 _tools/scenes.py /path [width]  -> shots/ucp-<page>-<tab>-<scene>.png"""
import sys, re
from pathlib import Path
from playwright.sync_api import sync_playwright
path = sys.argv[1]; w = int(sys.argv[2]) if len(sys.argv) > 2 else 1440
out = Path(__file__).parent / "shots"; out.mkdir(exist_ok=True)
slug = re.sub(r"\W+", "-", path.strip("/"))
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": w, "height": 1000})
    pg.goto("http://localhost:4610" + path, wait_until="networkidle")
    tabs = pg.locator(".om-tab")
    n_tabs = max(1, tabs.count())
    for t in range(n_tabs):
        if tabs.count(): tabs.nth(t).click()
        panel = pg.locator(".om-media [role=tabpanel]:not([hidden]) .ucp").first if tabs.count() else pg.locator(".ucp").first
        panel.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
        segs = panel.locator(".ucp-seg")
        for s in range(segs.count()):
            segs.nth(s).click(); pg.mouse.move(0, 0); pg.wait_for_timeout(4800)
            target = pg.locator(".om-media [role=tabpanel]:not([hidden])").first if tabs.count() else panel
            target.screenshot(path=str(out / f"ucp-{slug}-{t+1}-{s+1}.png"))
    b.close()
print("done")
