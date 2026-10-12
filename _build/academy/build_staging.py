"""Build the staged Academy sources with the real build.py (audit + output to public/), without touching _build/pages/.
usage: python3 _build/academy/build_staging.py [name,name...]"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import build  # noqa: E402
build.PAGES = HERE / "staging"
names = sys.argv[1] if len(sys.argv) > 1 else ",".join(p.stem for p in sorted(build.PAGES.glob("*.html")))
sys.argv = ["build.py", "--only", names]
sys.exit(build.main())
