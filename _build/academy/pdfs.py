"""Render each Academy guide to a PDF (print stylesheet) into _build/static/assets/academy/pdf/<slug>.pdf.
Needs the local preview server (python3 _build/serve.py) on :4610. usage: python3 _build/academy/pdfs.py"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).parent))
from render import DESK, FUND
OUT = Path(__file__).resolve().parents[1] / "static/assets/academy/pdf"
OUT.mkdir(parents=True, exist_ok=True)
paths = [(s, f"/guides/{s}") for s, *_ in DESK] + [(s, f"/pascal-academy/guides/{s}") for s, *_ in FUND]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    for slug, path in paths:
        pg.goto("http://localhost:4610" + path, wait_until="domcontentloaded")
        pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager'); document.querySelectorAll('details').forEach(d=>d.open=true)")
        pg.wait_for_timeout(1500)
        pg.emulate_media(media="print")
        pg.pdf(path=str(OUT / f"{slug}.pdf"), format="A4", print_background=True,
               display_header_footer=True, header_template="<span></span>",
               footer_template='<div style="font:8px Helvetica;color:#6B7979;width:100%;padding:0 14mm;display:flex;justify-content:space-between"><span>Pascal Academy · pascalailabs.com/pascal-academy</span><span class="pageNumber"></span></div>',
               margin={"top": "14mm", "bottom": "16mm", "left": "12mm", "right": "12mm"})
        print(slug, (OUT / f"{slug}.pdf").stat().st_size // 1024, "KB")
    b.close()
