"""Viewport screenshots down a local page. usage: snapv.py /path name [width] [n]"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
path,name=sys.argv[1],sys.argv[2]; w=int(sys.argv[3]) if len(sys.argv)>3 else 1440; n=int(sys.argv[4]) if len(sys.argv)>4 else 4
out=Path(__file__).parent/"shots"/"ac"; out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":w,"height":900})
    pg.goto("http://localhost:4610"+path,wait_until="domcontentloaded"); pg.wait_for_timeout(2500)
    pg.add_style_tag(content=".reveal{opacity:1!important;transform:none!important}")
    H=pg.evaluate("document.body.scrollHeight")
    for i in range(n):
        y=int(i*(H-900)/max(n-1,1)) if n>1 else 0
        pg.evaluate(f"document.documentElement.style.scrollBehavior=\"auto\";window.scrollTo(0,{y})"); pg.wait_for_timeout(350)
        pg.screenshot(path=str(out/f"{name}-{i}.png"))
    b.close()
from PIL import Image
ims=[Image.open(out/f"{name}-{i}.png") for i in range(n)]
sw=720; sh=int(900*sw/w)
sheet=Image.new('RGB',(sw*2,sh*((n+1)//2)),'white')
for i,im in enumerate(ims): sheet.paste(im.resize((sw,sh)),((i%2)*sw,(i//2)*sh))
sheet.save(out/f"sheet-{name}.png"); print(out/f"sheet-{name}.png", H)
