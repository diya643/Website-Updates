"""Writes partials/cg-twin.html: the context graph from the Pascal Digital Twin demo video
(digital-employee-video/scenes/02b-learn.html), as a static, CSS-animated component.
Run: python3 gen/cg_twin.py"""
from pathlib import Path
W, H = 1000, 640
N = {  # id: (kind, label, x%, y%, order)
    "hr": ("c", "The firm", 50, 50, 0),
    "f1": ("", "Fund I", 22, 16, 1), "f2": ("", "Fund II", 50, 13, 2), "f3": ("", "Fund III", 78, 16, 3),
    "mt": ("pp", "Michael Turner", 58, 31, 4), "sm": ("pp", "Sarah Mitchell", 35, 32, 5),
    "su": ("dl", "Project Summit", 13, 37, 6), "ha": ("dl", "Project Harbor", 11, 60, 7), "ma": ("dl", "Project Maple", 22, 82, 8),
    "fr": ("dl", "Project Frost", 82, 41, 9), "gl": ("dl", "Project Glacier", 82, 64, 10), "wr": ("dl", "Project Wren", 76, 83, 11),
    "cc": ("sc", "Cold chain", 68, 65, 12), "hs": ("sc", "Healthcare services", 31, 65, 13),
    "ic": ("tp", "IC memo template", 50, 90, 14), "hp": ("ad", "Harlow & Pike", 53, 74, 15),
}
E = [("hr","f1"),("hr","f2"),("hr","f3"),("hr","mt"),("hr","sm"),("hr","ic"),("f1","su"),("f1","ha"),("f2","su"),("f2","ma"),("f3","fr"),("f3","gl"),("f3","wr"),("fr","cc"),("gl","cc"),("fr","mt"),("ma","hs"),("ha","hs"),("wr","hp"),("fr","hp"),("ma","ic"),("sm","hs"),("cc","hp")]
seed = 7
def rnd():
    global seed
    seed = (seed * 16807) % 2147483647
    return seed / 2147483647
bokeh = []
for i in range(30):
    s = 10 + rnd() * 34; x = rnd() * 100; y = rnd() * 100
    c = "rgba(248,200,165,.16)" if rnd() > .5 else "rgba(141,226,181,.14)"
    bokeh.append(f'<i style="width:{s:.0f}px;height:{s:.0f}px;left:{x:.1f}%;top:{y:.1f}%;background:{c}"></i>')
paths = []
for k, (a, b) in enumerate(E):
    x1, y1 = N[a][2] / 100 * W, N[a][3] / 100 * H
    x2, y2 = N[b][2] / 100 * W, N[b][3] / 100 * H
    mx, my, dx, dy = (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1
    s = (1 if k % 2 else -1) * .22
    hot = " hot" if "fr" in (a, b) else ""
    d = .25 + max(N[a][4], N[b][4]) * .12 + .15
    paths.append(f'<path class="e{hot}" pathLength="1" style="--d:{d:.2f}s" d="M{x1:.0f} {y1:.0f} Q{mx - dy * s:.0f} {my + dx * s:.0f} {x2:.0f} {y2:.0f}"/>')
nodes = []
for nid, (kind, label, x, y, o) in N.items():
    cls = " ".join(c for c in ["cgt-nd", kind, "hot" if nid == "fr" else "", "lft" if x >= 75 else ""] if c)
    nodes.append(f'<span class="{cls}" style="left:{x}%;top:{y}%;--d:{.2 + o * .12:.2f}s"><b></b><span>{label.replace("&", "&amp;")}</span></span>')
canvas = f'''<div class="cgt-cv">
      <div class="cgt-bk" aria-hidden="true">{"".join(bokeh)}</div>
      <svg class="cgt-ed" viewBox="0 0 {W} {H}" aria-hidden="true">{"".join(paths)}</svg>
      {"".join(nodes)}
    </div>'''
pop = '''<div class="cgt-pop">
        <p class="cgt-pop-h">Project Frost <span class="pui-tag amber">Declined · Mar 2024</span></p>
        <dl><dt>Vote</dt><dd>4 to 1 at IC</dd><dt>Why</dt><dd>Top 3 customers at 58% of revenue. Capex at 12.4% of revenue.</dd><dt>Revisit if</dt><dd>Pharma mix is above 40%, per Michael Turner</dd><dt>Linked</dt><dd>Frost model v12 · IC minutes · 3 expert calls</dd></dl>
      </div>'''
label = ("Pascal's context graph of a private equity firm. The firm links to Fund I, II and III, partners, past deals such as "
         "Projects Summit, Harbor, Maple, Frost, Glacier and Wren, sectors such as cold chain and healthcare services, an advisor "
         "and the IC memo template. Project Frost is highlighted: declined at IC in March 2024 by 4 votes to 1 on customer "
         "concentration, to be revisited if the pharma mix rises above 40%. Pascal knows 41,600 deals screened, 6,850 IC memos and "
         "votes, 2,614,800 companies and people and 28 years of history.")
html = f'''<!--mock--><div class="cgt" data-cgt role="img" aria-label="{label}">
  <div class="cgt-win">
    <div class="cgt-bar"><!--#include pui-mark--><span class="pui-crumb">Your firm / Pascal / <b>Context graph</b></span></div>
    <div class="cgt-body">
      {canvas}
      <div class="cgt-side">
        <div class="cgt-box"><p class="pui-k">The firm, as Pascal knows it</p>
          <div class="cgt-sts"><p><b>41,600</b><span>deals screened</span></p><p><b>6,850</b><span>IC memos and votes</span></p><p><b>2,614,800</b><span>companies and people</span></p><p><b>28</b><span>years of history</span></p></div>
        </div>
        <div class="cgt-box cgt-q"><p class="pui-k">How the firm decides</p><p>Passes on <b>customer concentration above 50%</b> in 212 of 240 cases. Underwrites on <b>lease-adjusted net debt</b>. Partners back <b>healthcare services</b> most often.</p></div>
        {pop}
        <p class="cgt-done">{{{{icon:check}}}} Pascal is ready to work</p>
      </div>
    </div>
  </div>
</div><!--/mock-->
'''
Path(__file__).resolve().parent.parent.joinpath("partials/cg-twin.html").write_text(html)
print("wrote partials/cg-twin.html")
