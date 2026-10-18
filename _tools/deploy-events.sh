#!/bin/zsh
# Build and push the events preview to its own personal Vercel project, pascal-events-preview.
# Same static site as the product preview, but / redirects to /events so the link opens on the events.
set -e
ROOT=${0:A:h:h}
cd $ROOT/_build && python3 build.py > /dev/null || { echo "build has blocking issues"; exit 1; }
D=$ROOT/_deploy-events
mkdir -p $D && rm -rf $D/public && cp -R $ROOT/public $D/
python3 - "$ROOT/vercel.json" "$D/vercel.json" <<'PY'
import json, sys
v = json.load(open(sys.argv[1]))
v["outputDirectory"] = "public"
v.setdefault("redirects", []).insert(0, {"source": "/", "destination": "/events", "permanent": False})
# preview only: keep the vercel.app copy out of search indexes (production ships without this)
v.setdefault("headers", []).insert(0, {"source": "/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]})
json.dump(v, open(sys.argv[2], "w"), indent=2)
PY
python3 - "$D/public" <<'PY'
import re, sys, pathlib
for f in pathlib.Path(sys.argv[1]).rglob("*.html"):
    h = f.read_text()
    m = re.search(r'<a class="nav-link" href="/news"[^>]*>.*?</a>', h, re.S)
    if not m: continue
    news = m.group(0).replace('href="/news"', 'href="/events"')
    h = re.sub(r'<nav class="nav-links" aria-label="Main">.*?</nav>', '<nav class="nav-links" aria-label="Main"><div class="nav-item" data-menu>' + news + '<div class="mega mega-list mega-news"><div class="mega-panel"><div class="mn-col"><p class="mp-label">News</p><a class="mp-link" href="/events">Events</a></div></div></div></div></nav>', h, count=1, flags=re.S)
    h = re.sub(r'(<div class="mobile-menu" id="mobile-menu">).*?(<a class="btn btn-dark")', r'\1<details open><summary>News</summary><a href="/events">Events</a></details>\2', h, count=1, flags=re.S)
    cols = ('<nav aria-label="Product"><p class="fh">Product</p><ul><li><a href="/product">Product</a></li><li><a href="/#research-stack">Features</a></li></ul></nav>'
            '<nav aria-label="Company"><p class="fh">Company</p><ul><li><a href="/security">Security</a></li><li><a href="/about">About</a></li><li><a href="/careers">Careers</a></li></ul></nav>'
            '<nav aria-label="News"><p class="fh">News</p><ul><li><a href="/events">Events</a></li></ul></nav>'
            '<nav aria-label="Legal"><p class="fh">Legal</p><ul><li><a href="/terms-of-use">Terms of Use</a></li><li><a href="/privacy-policy">Privacy Policy</a></li></ul></nav>')
    h = re.sub(r'\s*<nav aria-label="(?:Platform|Products|Industries|News|Company)">.*?</nav>', '', h, flags=re.S)
    h = re.sub(r'(<p class="footer-blurb">.*?</p>\s*</div>)', lambda m: m.group(1) + cols, h, count=1, flags=re.S)
    f.write_text(h)
PY
cd $D
[ -d .vercel ] || vercel link --yes --project pascal-events-preview --scope ithinkmotomotolikesyou
vercel deploy --prod --yes
