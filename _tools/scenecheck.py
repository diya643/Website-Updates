"""Check every scene of every use-case player for overlapping text, clipped text and content taller than the stage.
usage: python3 _tools/scenecheck.py <width> [path ...]"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
pub = Path(__file__).resolve().parent.parent / "public"
w = int(sys.argv[1]); paths = sys.argv[2:] or sorted("/" + str(p.parent.relative_to(pub)) for p in pub.rglob("index.html"))
JS = r"""(args) => {
 const [ui, si] = args; const u = document.querySelectorAll('.ucp')[ui]; const out = [];
 const tp = u.closest('[role=tabpanel]'); if (tp) tp.hidden = false;
 const scenes = [...u.querySelectorAll('.ucp-scene')];
 scenes.forEach((s, k) => { s.style.display = k === si ? 'block' : 'none'; s.style.opacity = 1; s.style.visibility = 'visible'; s.style.transition = 'none'; });
 const s = scenes[si]; s.querySelectorAll('.ucp-in').forEach(e => { e.style.animation = 'none'; e.style.opacity = 1; });
 s.querySelectorAll('.ucp-type').forEach(e => { e.style.animation = 'none'; e.style.clipPath = 'none'; });
 const own = (e) => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1);
 const lab = (e) => (e.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 36);
 const texts = [...s.querySelectorAll('*')].filter(e => own(e) && e.getBoundingClientRect().width > 0);
 const I = (a, b) => Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left)) * Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
 for (let i = 0; i < texts.length; i++) for (let j = i + 1; j < texts.length; j++) {
  const a = texts[i], b = texts[j]; if (a.contains(b) || b.contains(a)) continue;
  const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect(), x = I(ra, rb);
  if (x > 12 && x > .15 * Math.min(ra.width * ra.height, rb.width * rb.height)) out.push('overlap: ' + lab(a) + ' <> ' + lab(b));
 }
 texts.forEach(t => { const cs = getComputedStyle(t); if (t.scrollWidth > t.clientWidth + 2 && cs.textOverflow !== 'ellipsis' && /hidden|clip/.test(cs.overflowX) && !t.classList.contains('ucp-type')) out.push('text cut: ' + lab(t)); });
 const stage = u.querySelector('.ucp-stage').getBoundingClientRect(); let bottom = 0, right = 0;
 s.querySelectorAll('*').forEach(e => { const r = e.getBoundingClientRect(); if (r.height) { bottom = Math.max(bottom, r.bottom); right = Math.max(right, r.right); } });
 if (bottom > stage.bottom + 1) out.push('taller than stage by ' + Math.round(bottom - stage.bottom) + 'px');
 if (right > stage.right + 1) out.push('wider than stage by ' + Math.round(right - stage.right) + 'px');
 return [(tp || {}).id || '', s.dataset.label || '', out];
}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": w, "height": 900})
    for path in paths:
        pg.goto("http://localhost:4610" + path, wait_until="networkidle")
        n = pg.evaluate("document.querySelectorAll('.ucp').length")
        for ui in range(n):
            m = pg.evaluate(f"document.querySelectorAll('.ucp')[{ui}].querySelectorAll('.ucp-scene').length")
            for si in range(m):
                tab, label, issues = pg.evaluate(JS, [ui, si])
                for i in issues: print(w, path, tab or f"ucp{ui}", f"scene {si+1} {label}", "|", i)
    b.close()
print("scenecheck done", w)
