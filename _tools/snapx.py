"""Screenshot an external URL (viewport crops). usage: snapx.py URL name [width] [n_screens]"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
url,name=sys.argv[1],sys.argv[2]; w=int(sys.argv[3]) if len(sys.argv)>3 else 1440; n=int(sys.argv[4]) if len(sys.argv)>4 else 3
out=Path(__file__).parent/"shots"/"live"; out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":w,"height":900})
    pg.goto(url,wait_until="domcontentloaded"); pg.wait_for_timeout(4000)
    pg.add_style_tag(content="[class*=cookie],[id*=cookie]{display:none!important}")
    H=pg.evaluate("document.body.scrollHeight")
    for i in range(n):
        y=int(i*(H-900)/max(n-1,1)) if n>1 else 0
        pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(500)
        pg.screenshot(path=str(out/f"{name}-{i}.png"))
    print(name,H)
    b.close()
