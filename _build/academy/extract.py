#!/usr/bin/env python3
"""Extract Pascal Academy content from the live Next.js pages into structured JSON.

    python3 _build/academy/extract.py

Reads the saved live HTML in website-v2/_academy_src/*.html (downloaded from pascalailabs.com on 11 Oct 2026)
and writes _build/academy/data/<slug>.json. The new templates (render.py) only change layout; the copy comes
from here verbatim, apart from fixes listed in TEXT_FIXES (encoding, em dashes, Pascal ban list).
"""
import html
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Comment, Tag

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent.parent / "_academy_src"
OUT = ROOT / "data"

# ---------------------------------------------------------------- text clean-up
MOJIBAKE = {"â\x80\x94": "—", "â\x80\x93": "–", "â\x80\x99": "’", "â\x80\x98": "‘", "â\x80\x9c": "“",
            "â\x80\x9d": "”", "â\x80¦": "…", "Â·": "·", "Â ": " "}
# Pascal writing ban list (build.py fails on these). Minimal, meaning-preserving swaps.
BANNED = [
    (r"\bhigh-leverage\b", "high-value"),
    (r"\bleverag(e|es|ed|ing)\b", lambda m: {"e": "use", "es": "uses", "ed": "used", "ing": "using"}[m.group(1)]),
    (r"\bLeverag(e|es|ed|ing)\b", lambda m: {"e": "Use", "es": "Uses", "ed": "Used", "ing": "Using"}[m.group(1)]),
    (r"\brobust\b", "reliable"), (r"\bRobust\b", "Reliable"),
    (r"\bseamless(ly)?\b", lambda m: "smoothly" if m.group(1) else "smooth"),
    (r"\bunlock(s|ed|ing)?\b", lambda m: "open" + (m.group(1) or "") if m.group(1) != "ing" else "opening"),
    (r"\bstreamlin(e|es|ed|ing)\b", lambda m: {"e": "simplify", "es": "simplifies", "ed": "simplified", "ing": "simplifying"}[m.group(1)]),
    (r"\bholistic\b", "complete"),
    (r"\b[Mm]oreover,?\s*", ""), (r"\b[Ff]urthermore,?\s*", ""),
    (r"\bunderscor(e|es|ed|ing)\b", lambda m: {"e": "highlight", "es": "highlights", "ed": "highlighted", "ing": "highlighting"}[m.group(1)]),
    (r"\bdelv(e|es|ed|ing)\b", lambda m: {"e": "dig", "es": "digs", "ed": "dug", "ing": "digging"}[m.group(1)]),
    (r"\bempower(s|ed|ing)?\b", lambda m: "enable" + {"": "", "s": "s", "ed": "d", "ing": ""}[m.group(1) or ""] if m.group(1) != "ing" else "enabling"),
    (r"\btransformative\b", "far-reaching"),
    (r"\bgroundbreaking\b", "new"),
    (r"\bcutting-edge\b", "leading"),
    (r"\brevolutioni[sz](e|es|ed|ing)\b", lambda m: {"e": "reshape", "es": "reshapes", "ed": "reshaped", "ing": "reshaping"}[m.group(1)]),
    (r"\bgame[- ]changer\b", "major shift"),
    (r"\bdeep dive\b", "detailed look"),
    (r"\bsynerg(y|ies)\b", lambda m: "fit" if m.group(1) == "y" else "fits"),
    (r"\bembark(s|ed|ing)?\b", lambda m: "start" + (m.group(1) or "")),
    (r"\bunpack(s|ed|ing)?\b", lambda m: "explain" + (m.group(1) or "")),
    (r"\bcompetitive landscapes\b", "competitors"), (r"\bcompetitive landscape\b", "competitive field"),
    (r"\b(market|vendor|competitive|regulatory|data|AI|technology|tooling) landscape\b", lambda m: m.group(1) + " map"),
    (r"\blandscape\b", "map"),
    (r"\bit's worth noting that\s*", ""), (r"\bIt's worth noting that\s*", ""),
]


def clean_text(s):
    for a, b in MOJIBAKE.items():
        s = s.replace(a, b)
    s = s.replace(" ", " ")
    for pat, rep in BANNED:
        s = re.sub(pat, rep, s)
    return s


def no_dash(s):
    """Site copy uses no em dashes. ' — ' becomes ': ' after a short lead-in label, otherwise ', '."""
    s = re.sub(r"\s*—\s*", " — ", s)
    if " — " not in s:
        return s
    head, _, tail = s.partition(" — ")
    if len(re.sub(r"<[^>]+>", "", head).split()) <= 4 and " — " not in tail:
        return head + ": " + tail
    s = re.sub(r" — ([^—.]{1,80}?) — ", r", \1, ", s)
    return s.replace(" — ", ", ")


# ---------------------------------------------------------------- html helpers
def soup_of(name):
    return BeautifulSoup((SRC / name).read_text(encoding="utf-8"), "html.parser")


def rsc_text(soup):
    """Concatenate the Next.js flight payload (holds props for collapsed content such as FAQ answers)."""
    parts = []
    for sc in soup.find_all("script"):
        t = sc.string or ""
        m = re.match(r'\s*self\.__next_f\.push\(\[1,"(.*)"\]\)\s*$', t, flags=re.S)
        if m:
            try:
                parts.append(json.loads('"' + m.group(1) + '"'))
            except json.JSONDecodeError:
                pass
    return "".join(parts)


def rsc_faqs(soup):
    txt = rsc_text(soup)
    out = []
    for m in re.finditer(r'\{"question":("(?:[^"\\]|\\.)*"),"answer":("(?:[^"\\]|\\.)*")\}', txt):
        q, a = json.loads(m.group(1)), json.loads(m.group(2))
        if (q, a) not in out:
            out.append((q, a))
    return out


def inline(el):
    """Children of el as clean inline HTML (a, strong, em, code, br only)."""
    out = []
    for c in el.children:
        if isinstance(c, Comment):
            continue
        if isinstance(c, NavigableString):
            out.append(html.escape(str(c), quote=False))
            continue
        if not isinstance(c, Tag) or c.name in ("svg", "script", "style", "button"):
            continue
        inner = inline(c)
        if c.name == "a" and c.get("href"):
            href = c["href"].replace("https://pascalailabs.com", "") or "/"
            out.append(f'<a href="{html.escape(href)}">{inner}</a>')
        elif c.name in ("strong", "b"):
            out.append(f"<strong>{inner}</strong>")
        elif c.name in ("em", "i"):
            out.append(f"<em>{inner}</em>")
        elif c.name == "code":
            out.append(f"<code>{inner}</code>")
        elif c.name == "br":
            out.append("<br>")
        else:
            out.append(inner)
    s = re.sub(r"\s+", " ", "".join(out))
    return s


def tidy(s):
    s = clean_text(s)
    s = no_dash(s)
    s = re.sub(r"\s+([,.;:])", r"\1", s).strip()
    s = re.sub(r"<strong>\s*</strong>|<em>\s*</em>", "", s)
    return s


def text(el):
    return tidy(" ".join(el.get_text(" ").split())) if el is not None else ""


# ---------------------------------------------------------------- docs (guides + fundamentals)
CALLOUT_KINDS = [("pascal academy", "academy"), ("summary", "summary"), ("optional", "deeper"), ("go deeper", "deeper"),
                 ("key principle", "principle"), ("key takeaway", "principle"), ("why this matters", "matters"),
                 ("mistake", "warning"), ("security", "warning"), ("warning", "warning"), ("tip", "tip"),
                 ("example", "example"), ("in practice", "example")]
ACRONYMS = ["AI", "LLM", "LLMs", "RAG", "GraphRAG", "MCP", "KV", "API", "APIs", "RDF", "RLHF", "ReAct", "MNPI", "IC", "PE",
            "CIM", "DCF", "HNSW", "JSON", "SQL", "GPT", "Pascal", "Pascal Academy", "Claude", "Gemini", "OpenAI"]


def sentence_case(t):
    t = t[:1].upper() + t[1:].lower()
    for a in ACRONYMS:
        t = re.sub(rf"\b{re.escape(a.lower())}\b", a, t, flags=re.I) if a not in ("IC", "PE") else t
    return t[:1].upper() + t[1:]


def callout(aside):
    kids = [c for c in aside.find_all(recursive=False) if isinstance(c, Tag)]
    label = ""
    if kids and kids[0].name == "p" and "uppercase" in " ".join(kids[0].get("class", [])):
        label = " ".join(kids[0].get_text(" ").split())
        kids[0].extract()
    kind = "note"
    for k, v in CALLOUT_KINDS:
        if k in label.lower():
            kind = v
            break
    if label.isupper():
        label = sentence_case(label)
    return {"t": "callout", "kind": kind, "label": tidy(html.escape(label, quote=False)), "blocks": blocks(aside)}


def table(el):
    t = el if el.name == "table" else el.find("table")
    head = [tidy(inline(th)) for th in t.select("thead th")]
    rows = []
    for tr in t.select("tbody tr") or t.find_all("tr")[1 if head else 0:]:
        cells = []
        for td in tr.find_all(["td", "th"]):
            h = tidy(inline(td))
            bar = td.find(style=re.compile(r"width:\s*\d"))
            if not h and bar is not None:  # visual likelihood bar on the live page
                w = re.search(r"width:\s*([\d.]+)%", bar["style"]).group(1)
                h = f'<span class="ac-meter" style="--w:{w}%" role="img" aria-label="{w}% relative likelihood"></span>'
            cells.append(h)
        rows.append(cells)
    return {"t": "table", "head": head, "rows": rows}


def li_html(li):
    sub = [c for c in li.children if isinstance(c, Tag) and c.name in ("ul", "ol")]
    for s in sub:
        s.extract()
    h = tidy(inline(li))
    for s in sub:
        h += f"<{s.name}>" + "".join(f"<li>{li_html(x)}</li>" for x in s.find_all("li", recursive=False)) + f"</{s.name}>"
    return h


def blocks(el, anchor=None):
    out = []
    for c in el.children:
        if not isinstance(c, Tag):
            if isinstance(c, NavigableString) and c.strip() and not isinstance(c, Comment):
                out.append({"t": "p", "h": tidy(html.escape(c.strip(), quote=False))})
            continue
        n = c.name
        if n in ("nav", "button", "svg", "script", "style", "header", "img", "figure"):
            continue
        if n == "p":
            h = tidy(inline(c))
            if h:
                out.append({"t": "p", "h": h})
        elif n in ("h2", "h3", "h4", "h5"):
            out.append({"t": n if n != "h5" else "h4", "h": tidy(inline(c)), "id": c.get("id") or anchor})
            anchor = None
        elif n in ("ul", "ol"):
            items = [li_html(li) for li in c.find_all("li", recursive=False)]
            out.append({"t": n, "items": [i for i in items if i]})
        elif n == "table" or (n == "div" and c.find("table") and not c.find(["p", "h2", "h3"])):
            out.append(table(c))
        elif n == "aside":
            out.append(callout(c))
        elif n == "pre":
            out.append({"t": "pre", "h": html.escape(clean_text(c.get_text()).strip("\n"), quote=False)})
        elif n == "blockquote":
            out.append({"t": "quote", "blocks": blocks(c)})
        elif n in ("div", "section", "article", "span", "main"):
            sub = blocks(c, anchor=c.get("id") or anchor)
            if c.get("id") and sub and sub[0]["t"] in ("h3", "h4") and not sub[0].get("id"):
                sub[0]["id"] = c["id"]
            out += sub
        else:
            h = tidy(inline(c))
            if h:
                out.append({"t": "p", "h": h})
    return out


def doc(src, slug, kind, path):
    s = soup_of(src)
    art = s.find("article")
    header = s.find("header")
    h1s = s.find_all("h1")
    title = text(h1s[-1])
    # dek + meta line
    dek, meta_line, subtitle = "", "", ""
    hdr = h1s[-1].parent
    ps = [text(p) for p in hdr.find_all("p")]
    for p in ps:
        if re.search(r"\bmin read\b", p):
            meta_line = p
        elif not dek and p != title:
            dek = p
    if kind == "desk":
        # desk guides: <header> holds h1 + subtitle; article holds intro paragraphs then TOC then sections
        hp = header.find("p") if header else None
        subtitle = text(hp) if hp else ""
        mp = [text(p) for p in art.find_all("p", limit=6) if re.search(r"\bmin read\b", p.get_text())]
        meta_line = mp[0] if mp else ""
    # everything in the article in order; sections with ids become chapters
    intro, chapters, faq_q, outro, about = [], [], [], [], []
    container = art
    started = False
    for sec in container.find_all(["section", "nav"], recursive=True):
        pass
    toc = art.find("nav")
    # intro = blocks before the TOC nav that are not the header copy
    if toc is not None:
        for prev in toc.find_all_previous(["p", "ul", "ol"]):
            if art not in prev.parents:
                break
        before = []
        node = toc
        sib = toc.previous_sibling
        while sib is not None:
            if isinstance(sib, Tag):
                before.insert(0, sib)
            sib = sib.previous_sibling
        for b in before:
            if b.name == "header":
                continue
            for blk in blocks(b) if b.name != "p" else [{"t": "p", "h": tidy(inline(b))}]:
                if blk["t"] == "p" and (blk["h"] in (dek, meta_line, subtitle, title) or re.search(r"\bmin read\b", blk["h"])):
                    continue
                if blk["t"] in ("h1",):
                    continue
                intro.append(blk)
    for sec in art.find_all("section"):
        if sec.find_parent("section") is not None:
            continue
        sid = sec.get("id")
        h2 = sec.find("h2")
        if sid == "faq" or (h2 and re.match(r"(frequently asked|faq)", h2.get_text().strip(), re.I)):
            faq_q = [text(b.find("span") or b) for b in sec.find_all("button")]
            continue
        if h2 is None:
            bl = blocks(sec)
            if bl and bl[0]["t"] == "p" and bl[0]["h"].lower() == "pascal academy":
                outro = bl[1:]
            else:
                about += bl
            continue
        h2.extract()
        bl = blocks(sec)
        heading = tidy(inline(h2))
        heading = re.sub(r"^\d+\.\s*", "", heading)
        if re.match(r"about (the author|this guide)", heading, re.I):
            about = bl
            continue
        chapters.append({"id": sid or re.sub(r"\W+", "-", heading.lower()).strip("-"), "h": heading, "blocks": bl})
    # desk guides: the about block sits outside sections
    if not about:
        for h in art.find_all(["h2", "h3"]):
            if re.match(r"about (the author|this guide)", h.get_text().strip(), re.I):
                about = [{"t": "p", "h": text(p)} for p in h.find_all_next("p", limit=4) if art in p.parents]
                break
    faqs = rsc_faqs(s)
    if faq_q:
        byq = {q: a for q, a in faqs}
        faqs = [(q, byq.get(q, "")) for q in faq_q] + [(q, a) for q, a in faqs if q not in faq_q]
    faqs = [(tidy(html.escape(q, quote=False)), tidy(html.escape(a, quote=False))) for q, a in faqs if a]
    if kind == "desk":
        if re.search(r"\bmin read\b", subtitle):
            meta_line, subtitle = subtitle, ""
        meta_line = meta_line or f"{DESK_READ[slug]} min read"
        if not subtitle and intro and intro[0]["t"] == "p":
            dek = intro.pop(0)["h"]
        elif subtitle:
            dek, subtitle = subtitle, ""
        keep = []
        for c in chapters:
            if c["id"] == "about-the-author" or c["h"].lower().startswith("about pascal"):
                about = c["blocks"]
            else:
                keep.append(c)
        chapters = keep
    # bylines: the Academy is the author; dates stay
    about = [b for b in about if not re.match(r"Written by ", b.get("h", ""))] + [
        {"t": "updated", "h": m.group(1)} for b in about for m in [re.search(r"Updated (\w+ \d+, \d{4})", b.get("h", ""))] if m]
    outro = [b for b in outro if not b.get("h", "").endswith("→")]
    return {"kind": kind, "slug": slug, "path": path, "title": title, "subtitle": subtitle, "dek": dek,
            "meta": meta_line, "intro": intro, "chapters": chapters, "faqs": faqs, "outro": outro, "about": about}


DESK_READ = {"ai-for-hedge-funds": 24, "ai-for-asset-management": 20, "ai-for-investment-banking": 21,
             "ai-for-private-equity": 22}  # from the live Academy hub cards
DOCS = [
    ("guides_ai-for-hedge-funds.html", "ai-for-hedge-funds", "desk", "/guides/ai-for-hedge-funds"),
    ("guides_ai-for-asset-management.html", "ai-for-asset-management", "desk", "/guides/ai-for-asset-management"),
    ("guides_ai-for-investment-banking.html", "ai-for-investment-banking", "desk", "/guides/ai-for-investment-banking"),
    ("guides_ai-for-private-equity.html", "ai-for-private-equity", "desk", "/guides/ai-for-private-equity"),
] + [(f"g_{s}.html", s, "fundamentals", f"/pascal-academy/guides/{s}") for s in [
    "large-language-models", "prompt-engineering", "rag-retrieval-augmented-generation", "ai-agents",
    "context-windows", "knowledge-graphs", "ai-hallucinations", "reasoning-models", "embeddings",
    "model-context-protocol"]]


# ---------------------------------------------------------------- library pages
def words_of(el):
    return [tidy(html.escape(" ".join(t.split()), quote=False)) for t in el.find_all(string=True)
            if t.strip() and not isinstance(t, Comment) and t.parent.name not in ("script", "style")]


def page_faqs(main):
    out = []
    for b in main.find_all("button", attrs={"aria-expanded": True}):
        art = b.parent
        p = art.find("p")
        q = " ".join(b.get_text(" ").replace("+", " ").replace("×", " ").split())
        if p is not None and q.endswith("?"):
            out.append((tidy(html.escape(q, quote=False)), tidy(inline(p))))
    return out


def glossary():
    s = soup_of("pascal-academy_ai-glossary.html")
    main = s.find("main")
    groups = []
    for h3 in main.find_all("h3"):
        head = h3.find_parent("div").find_parent("div")
        desc = head.find("p")
        grid = head.find_next_sibling("div")
        terms = []
        for art in grid.find_all("article"):
            sp = art.find("button").find("span")
            bits = [x for x in words_of(sp) if x not in ("+",)]
            terms.append({"term": bits[0], "tag": bits[1] if len(bits) > 1 else "", "def": tidy(inline(art.find("p")))})
        groups.append({"name": text(h3), "desc": text(desc), "terms": terms})
    return {"groups": groups, "faqs": page_faqs(main)}


def workflows():
    s = soup_of("pascal-academy_workflows.html")
    main = s.find("main")
    stages = []
    for b in main.select("section")[1].find_all("button"):
        w = words_of(b)
        # [n, name, question, name, description]
        stages.append({"n": w[0], "name": w[1], "q": w[2], "d": w[-1]})
    cats = []
    for h3 in main.find_all("h3"):
        head = h3.find_parent("div").find_parent("div")
        desc = head.find("p")
        grid = head.find_next_sibling("div")
        items = []
        for art in grid.find_all("article"):
            btn = art.find("button")
            name_el = btn.find("span", id=True) or btn.find("span")
            body = btn.find_next_sibling("div")
            steps = [text(li.find("strong") or li) for li in body.find_all("li")]
            flow = [" ".join(x.get_text(" ").split()) for x in body.select("ol + div > span > span:first-child")]
            if not flow:
                flow = [w for w in words_of(body.find("ol").find_next_sibling("div")) if w != "→"]
            io = {}
            for lab in body.find_all("span"):
                t = lab.get_text().strip()
                if t in ("Inputs", "Output") and lab.parent.name == "div":
                    io[t.lower()] = tidy(html.escape(" ".join(lab.parent.get_text(" ").split())[len(t):].strip(), quote=False))
            items.append({"id": name_el.get("id") or re.sub(r"\W+", "-", name_el.get_text().lower()).strip("-"),
                          "title": text(name_el), "desc": text(btn.find("p")), "steps": steps, "flow": flow,
                          "inputs": io.get("inputs", ""), "output": io.get("output", "")})
        cats.append({"name": text(h3), "desc": text(desc), "items": items})
    return {"stages": stages, "cats": cats}


def prompts():
    s = soup_of("pascal-academy_prompt-library.html")
    main = s.find("main")
    items = []
    for art in main.find_all("article"):
        btn = art.find("button")
        w = words_of(btn.find("div"))
        items.append({"cat": w[0], "n": w[1], "title": text(art.find("h3")), "when": text(art.find("p")),
                      "prompt": html.escape(clean_text(art.find("pre").get_text()).strip(), quote=False)})
    comps = []
    for sp in main.find_all("span"):
        st = sp.find("strong", recursive=False)
        if st is not None:
            comps.append({"k": text(st), "v": tidy(html.escape(" ".join(sp.get_text(" ").split())[len(st.get_text().strip()):].strip(), quote=False))})
    mistakes, bounds = [], []
    for sec in main.find_all("section"):
        h2 = sec.find("h2")
        if not h2:
            continue
        for d in sec.find_all("div"):
            kids = [c for c in d.children if isinstance(c, Tag) or (isinstance(c, NavigableString) and c.strip())]
            if len(kids) == 2 and isinstance(kids[0], NavigableString) and isinstance(kids[1], Tag) and kids[1].name == "p":
                item = {"k": tidy(html.escape(kids[0].strip(), quote=False)), "v": tidy(inline(kids[1]))}
                (bounds if "should not" in h2.get_text() else mistakes).append(item)
    # the unprettified source nests the label in its own element; fall back to label+p pairs
    if not mistakes:
        for sec in main.find_all("section"):
            h2 = sec.find("h2")
            if not h2:
                continue
            for p in sec.find_all("p"):
                lab = p.find_previous_sibling()
                if lab is not None and lab.name in ("div", "span", "h4") and p.parent.find("h2") is None and len(lab.get_text().split()) <= 6 and not lab.find("p"):
                    item = {"k": text(lab), "v": tidy(inline(p))}
                    (bounds if "should not" in h2.get_text() else mistakes).append(item)
    return {"items": items, "components": comps, "mistakes": mistakes, "bounds": bounds, "faqs": page_faqs(main)}


def libs():
    for name, fn in [("glossary", glossary), ("workflows", workflows), ("prompts", prompts)]:
        d = fn()
        (OUT / f"lib-{name}.json").write_text(json.dumps(d, indent=1, ensure_ascii=False))
        print(name, {k: (len(v) if isinstance(v, list) else v) for k, v in d.items()})


def main():
    OUT.mkdir(exist_ok=True)
    only = sys.argv[1:] or None
    for src, slug, kind, path in DOCS:
        if only and slug not in only:
            continue
        d = doc(src, slug, kind, path)
        (OUT / f"{slug}.json").write_text(json.dumps(d, indent=1, ensure_ascii=False))
        n = sum(len(re.sub(r"<[^>]+>", " ", json.dumps(c)).split()) for c in d["chapters"])
        print(f"{slug:38} ch={len(d['chapters']):2} intro={len(d['intro']):2} faqs={len(d['faqs'])} about={len(d['about'])} outro={len(d['outro'])} words~{n}")


if __name__ == "__main__":
    main()
    libs()
