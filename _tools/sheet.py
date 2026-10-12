"""Contact sheet of every shot matching a prefix: python3 _tools/sheet.py <prefix>"""
import sys
from pathlib import Path
from PIL import Image
d = Path(__file__).parent / "shots"
fs = sorted(d.glob(sys.argv[1] + "*.png")); ims = [Image.open(f) for f in fs if "sheet" not in f.name]
W = 600; ims = [i.resize((W, int(i.height * W / i.width))) for i in ims]
H = max(i.height for i in ims); sheet = Image.new("RGB", (W * len(ims), min(H, 6000)), "white")
for k, i in enumerate(ims): sheet.paste(i, (k * W, 0))
o = d / f"sheet-{sys.argv[1]}.png"; sheet.save(o); print(o)
