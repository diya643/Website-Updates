"""Sentence coverage of each live Academy page on its rebuilt page. usage: python3 _build/academy/coverage.py [-v]"""
import re, sys, html
from pathlib import Path
from bs4 import BeautifulSoup
sys.path.insert(0, str(Path(__file__).parent))
from extract import clean_text, rsc_faqs, soup_of
R = Path(__file__).resolve().parents[2]
MAP = {"pascal-academy.html": "pascal-academy", "pascal-academy_ai-fundamentals.html": "pascal-academy/ai-fundamentals",
       "pascal-academy_ai-glossary.html": "pascal-academy/ai-glossary", "pascal-academy_workflows.html": "pascal-academy/workflows",
       "pascal-academy_prompt-library.html": "pascal-academy/prompt-library", "pascal-academy_agent-library.html": "pascal-academy/agent-library"}
for f in (R / "_academy_src").glob("guides_*.html"):
    MAP[f.name] = "guides/" + f.stem.split("_", 1)[1]
for f in (R / "_academy_src").glob("g_*.html"):
    MAP[f.name] = "pascal-academy/guides/" + f.stem[2:]
norm = lambda x: re.sub(r"[^a-z0-9]", "", clean_text(x).lower().replace("’", "'"))
def sentences(t):
    t = re.sub(r"\s+", " ", t)
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+(?=[A-Z“\"])", t) if len(s.split()) >= 6]
tot_ok = tot = 0
for src, path in sorted(MAP.items()):
    s = soup_of(src); m = s.find("main") or s.body
    for t in m(["script", "style", "svg"]): t.decompose()
    blocks = [" ".join(el.get_text(" ").split()) for el in m.find_all(["p", "li", "td", "th", "h1", "h2", "h3", "pre", "span"]) if not el.find(["p", "li", "div"])]
    blocks += [a for q, a in rsc_faqs(soup_of(src))]
    sents = list(dict.fromkeys(x for b in blocks for x in sentences(b)))
    page = BeautifulSoup((R / "public" / path / "index.html").read_text(), "html.parser").find("main")
    for t in page(["script", "style", "svg"]): t.decompose()
    P = norm(page.get_text(" "))
    miss = [x for x in sents if norm(x)[:50] not in P and norm(x)[-40:] not in P]
    tot += len(sents); tot_ok += len(sents) - len(miss)
    print(f"{path:52} {len(sents) - len(miss):4}/{len(sents):<4} {100 * (len(sents) - len(miss)) // max(1, len(sents))}%")
    if "-v" in sys.argv:
        for x in miss: print("     -", x[:150])
print(f"TOTAL {tot_ok}/{tot} = {100 * tot_ok / tot:.1f}%")
