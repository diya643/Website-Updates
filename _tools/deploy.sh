#!/bin/zsh
# Build and push the product + solutions preview to the personal Vercel project pascal-product-preview.
set -e
ROOT=${0:A:h:h}
cd $ROOT/_build && python3 build.py > /dev/null || { echo "build has blocking issues"; exit 1; }
D=$ROOT/_deploy
mkdir -p $D && rm -rf $D/public && cp -R $ROOT/public $D/
python3 - "$ROOT/vercel.json" "$D/vercel.json" <<'PY'
import json, sys
v = json.load(open(sys.argv[1]))
v["outputDirectory"] = "public"
# preview only: keep the vercel.app copy out of search indexes (production ships without this)
v.setdefault("headers", []).insert(0, {"source": "/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]})
json.dump(v, open(sys.argv[2], "w"), indent=2)
PY
cd $D
[ -d .vercel ] || vercel link --yes --project pascal-product-preview --scope ithinkmotomotolikesyou
vercel deploy --prod --yes
