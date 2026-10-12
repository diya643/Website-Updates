"""Find visual glitches in product mockups: overlapping text, floats covering content,
player scenes taller than their stage, and text overflowing its own box.
usage: python3 _tools/glitch.py <width> [path ...]   (all built pages when no path)"""
import sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright
pub = Path(__file__).resolve().parent.parent / "public"
w = int(sys.argv[1]); paths = sys.argv[2:] or sorted("/" + str(p.parent.relative_to(pub)) for p in pub.rglob("index.html"))
JS = r"""() => {
 const out = [];
 const vis = (e) => { for (let n = e; n && n !== document.body; n = n.parentElement) { const s = getComputedStyle(n); if (s.display === 'none' || s.visibility === 'hidden' || +s.opacity === 0) return false; } return true; };
 const own = (e) => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1);
 const label = (e) => (e.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 40);
 const R = (e) => { const r = e.getBoundingClientRect(); return r; };
 const inter = (a, b) => Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left)) * Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
 document.querySelectorAll('.pui').forEach((pui, pi) => {
  if (!vis(pui)) return;
  const id = (pui.closest('section[id]') || {}).id || ('pui' + pi);
  const texts = [...pui.querySelectorAll('*')].filter(e => own(e) && vis(e) && R(e).width > 0);
  // 1. text over text
  for (let i = 0; i < texts.length; i++) for (let j = i + 1; j < texts.length; j++) {
   const a = texts[i], b = texts[j]; if (a.contains(b) || b.contains(a)) continue;
   const ra = R(a), rb = R(b), x = inter(ra, rb);
   if (x > 12 && x > 0.15 * Math.min(ra.width * ra.height, rb.width * rb.height)) out.push(['overlap', id, label(a), label(b)]);
  }
  // 2. floats covering text in the window underneath
  pui.querySelectorAll('.pui-float').forEach(f => { if (!vis(f)) return; const rf = R(f);
   texts.filter(t => !f.contains(t)).forEach(t => { const rt = R(t); if (inter(rf, rt) > 0.3 * rt.width * rt.height) out.push(['float-covers', id, label(f).slice(0, 20), label(t)]); }); });
  // 3. text overflowing its own box (cut off without an ellipsis)
  texts.forEach(t => { const s = getComputedStyle(t); if (t.scrollWidth > t.clientWidth + 2 && s.textOverflow !== 'ellipsis' && (s.overflow === 'hidden' || s.overflowX === 'hidden')) out.push(['text-clipped', id, label(t), '']); });
 });
 return out;
}"""
SCENES = r"""() => {
 const out = [];
 document.querySelectorAll('.ucp').forEach((u, ui) => {
  const id = (u.closest('[role=tabpanel]') || u.closest('section[id]') || {}).id || ('ucp' + ui);
  const stage = u.querySelector('.ucp-stage'); if (!stage) return;
  [...u.querySelectorAll('.ucp-scene')].forEach((s, si) => {
   const pad = parseFloat(getComputedStyle(s).paddingBottom) || 0;
   let bottom = 0; s.querySelectorAll('*').forEach(e => { const r = e.getBoundingClientRect(); if (r.height) bottom = Math.max(bottom, r.bottom); });
   const limit = stage.getBoundingClientRect().bottom;
   if (bottom > limit + 1) out.push(['scene-clipped', id, 'scene ' + (si + 1) + ' ' + (s.dataset.label || ''), Math.round(bottom - limit) + 'px']);
  });
 });
 return out;
}"""
FORCE = ".ucp-scene{opacity:1!important;visibility:visible!important;transition:none!important} .ucp-in{opacity:1!important;animation:none!important} .ucp-type{clip-path:none!important;animation:none!important}"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": w, "height": 900})
    for path in paths:
        pg.goto("http://localhost:4610" + path, wait_until="networkidle"); pg.wait_for_timeout(300)
        found = pg.evaluate(JS)
        # scenes: make every scene visible one at a time is costly; check heights with all forced visible
        pg.add_style_tag(content=FORCE)
        found += pg.evaluate(SCENES)
        # every tab panel too
        for k in range(pg.locator('.om-tab').count()):
            pg.locator('.om-tab').nth(k).click(); pg.wait_for_timeout(100)
        seen = set()
        for f in found:
            key = tuple(f)
            if key in seen: continue
            seen.add(key); print(w, path, " | ".join(map(str, f)))
    b.close()
print("glitch check done", w)
