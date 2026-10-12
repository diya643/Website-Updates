#!/usr/bin/env python3
"""Render Pascal Academy page sources from the extracted JSON (data/*.json).

    python3 _build/academy/render.py            # writes _build/academy/staging/academy-*.html
    python3 _build/academy/render.py --promote  # copies them into _build/pages/ (only after they pass)

Then build them like any other page: python3 _build/build.py --only academy-hub,academy-...
Layout follows Glean: the Content Hub for the Academy home, the long-form article (sticky table of contents)
for guides, and the developer docs (left tree, "on this page", prev/next) for the fundamentals series.
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
STAGING = ROOT / "staging"
PAGES = ROOT.parent / "pages"

SIGNUP = "/pascal-academy/signup"
CUR = ' aria-current="page"'
LAZY = ' loading="lazy"'
HUB = "/pascal-academy"

DESK = [  # slug, short label, hub description (live hub copy), screenshot, panel
    ("ai-for-hedge-funds", "Hedge funds",
     "Research workflows, earnings analysis, company primers, modelling and investment idea generation.",
     ("shot-agent-table.webp", 1600, 844, "Pascal agent output: a street vs management framing table for Sea Limited with citations"), "panel-dark"),
    ("ai-for-asset-management", "Asset management",
     "Portfolio monitoring, research, earnings workflows, knowledge management and risk analysis.",
     ("shot-citations.webp", 1600, 844, "Pascal answer with numbered citations beside the source presentation"), "panel-cream"),
    ("ai-for-investment-banking", "Investment banking",
     "Pitch books, comparable companies, CIM analysis, due diligence and valuation support.",
     ("shot-ppt.webp", 1270, 585, "PowerPoint slide drafted by Pascal: gross margin expansion story"), "panel-cream"),
    ("ai-for-private-equity", "Private equity",
     "Deal sourcing, commercial due diligence, market mapping, portfolio monitoring and investment memos.",
     ("shot-word.webp", 1316, 660, "Word document drafted by Pascal: growth, constraints and forward debate"), "panel-dark"),
]
FUND = [  # slug, nav label, index description (live AI Fundamentals copy)
    ("large-language-models", "Large language models (LLMs)",
     "A beginner-friendly guide to the machinery behind ChatGPT, Claude, Gemini, and Llama."),
    ("prompt-engineering", "Prompt engineering", "A practical guide to steering large language models."),
    ("rag-retrieval-augmented-generation", "Retrieval-augmented generation (RAG)",
     "How grounding language models in external knowledge reduces hallucination and keeps responses current."),
    ("ai-agents", "AI agents",
     "How language models move from answering questions to pursuing goals, using tools, and completing multi-step tasks."),
    ("context-windows", "Context windows",
     "How much text a language model can hold in mind at once, why bigger is not always better, and what happens when you run out of room."),
    ("knowledge-graphs", "Knowledge graphs",
     "How structured relationships between entities give AI systems grounded, queryable knowledge that goes beyond text retrieval."),
    ("ai-hallucinations", "Hallucinations",
     "Why language models make things up, what causes confident but wrong output, and the techniques that reduce it."),
    ("reasoning-models", "Reasoning models",
     "How test-time compute lets language models think through hard problems, and what the trade-offs look like."),
    ("embeddings", "Embeddings",
     "How text becomes numbers, why similarity in vector space mirrors similarity in meaning, and the infrastructure that makes retrieval possible."),
    ("model-context-protocol", "Model Context Protocol (MCP)",
     "The open standard for connecting AI models to external tools, data sources, and services through a universal interface."),
]
LIB = [  # path, label, hub description (live hub copy)
    ("/pascal-academy/ai-glossary", "AI glossary", "An A-to-Z reference of AI terms written for investment teams."),
    ("/pascal-academy/workflows", "Workflows", "Step-by-step ways to apply AI to real tasks."),
    ("/pascal-academy/prompt-library", "Prompt library", "Tested prompts for research, memos and modelling."),
    ("/pascal-academy/agent-library", "Agent library", "Multi-step research agents for investment teams."),
]

# SEO meta, adapted from the live titles/descriptions to the build's limits (title <= 60, description 120-160)
SEO = {
    "ai-for-hedge-funds": ("AI for Hedge Funds: Use Cases and Implementation", "A practical guide to AI for hedge funds: use cases, benefits, challenges and implementation, from research automation and portfolio monitoring to production."),
    "ai-for-asset-management": ("AI for Asset Management: Use Cases and Implementation", "A practical guide to AI for asset managers: RFP automation, research, portfolio monitoring, compliant client reporting, and the architecture to run it safely."),
    "ai-for-investment-banking": ("AI for Investment Banking | Pascal Academy", "How AI supports investment banking: pitch books, comparable companies, industry research, CIM analysis, due diligence, valuation support and client decks."),
    "ai-for-private-equity": ("AI for Private Equity | Pascal Academy", "How AI supports the private equity lifecycle: deal sourcing, commercial due diligence, market mapping, investment memos and portfolio monitoring."),
    "large-language-models": ("Large Language Models Explained | Pascal Academy", "A beginner-friendly guide to large language models for finance teams: how LLMs work, what tokens are, how transformers process text, and where they fit."),
    "prompt-engineering": ("Prompt Engineering Guide for Finance | Pascal Academy", "A practical guide to prompt engineering for finance professionals: prompt anatomy, techniques, parameters and failure modes for better outputs from AI tools."),
    "rag-retrieval-augmented-generation": ("RAG (Retrieval-Augmented Generation) | Pascal Academy", "A complete guide to retrieval-augmented generation for finance teams: the RAG pipeline, embeddings, chunking, retrieval, grounding and agentic RAG."),
    "ai-agents": ("AI Agents Explained for Finance | Pascal Academy", "A guide to AI agents for finance: agent anatomy, the ReAct loop, planning, multi-agent systems, failure modes and how production agents work in research."),
    "context-windows": ("Context Windows Explained | Pascal Academy", "A guide to context windows for finance teams: what fills them, why there is a limit, lost-in-the-middle, cost and latency, and managing long documents."),
    "knowledge-graphs": ("Knowledge Graphs Explained | Pascal Academy", "A guide to knowledge graphs for finance teams: nodes, edges and properties, how graphs work, GraphRAG, and how they compare to vector databases for research."),
    "ai-hallucinations": ("AI Hallucinations Explained | Pascal Academy", "A guide to AI hallucinations for finance teams: why models hallucinate, how to detect it, and the techniques that reduce it in investment research."),
    "reasoning-models": ("Reasoning Models Explained | Pascal Academy", "A guide to AI reasoning models for finance teams: how they differ from standard LLMs, how test-time compute works, and where they add value."),
    "embeddings": ("Embeddings Explained | Pascal Academy", "A guide to embeddings for finance teams: what embeddings are, how they power semantic search and retrieval, and how they are used in investment research."),
    "model-context-protocol": ("Model Context Protocol (MCP) Explained | Pascal Academy", "A guide to the Model Context Protocol for finance teams: what MCP is, how it connects AI models to data sources like Bloomberg and Capital IQ."),
}


def esc(s):
    return html.escape(s, quote=True)


def load(name):
    return json.loads((DATA / f"{name}.json").read_text())


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", s).lower()).strip("-")


def front(meta):
    return "<!--meta\n" + json.dumps(meta, indent=1, ensure_ascii=False) + "\n-->\n"


def mins(meta_line):
    m = re.search(r"(\d+)\s*min", meta_line)
    return int(m.group(1)) if m else None


ICON = {"principle": "target", "summary": "list-checks", "deeper": "layers", "academy": "book-open", "tip": "zap",
        "warning": "alert", "matters": "flag", "example": "file-text", "note": "message"}


HEADING_FIX = {"RAG Instead of Stuffing": "Retrieve with RAG"}


def render_blocks(bl, h3cls="ac-h3"):
    out = []
    for b in bl:
        t = b["t"]
        if t == "p":
            out.append(f"<p>{b['h']}</p>")
        elif t in ("h3", "h4"):
            b = dict(b, h=HEADING_FIX.get(b["h"], b["h"]))
            hid = b.get("id") or slugify(b["h"])
            out.append(f'<h3 id="{esc(hid)}">{b["h"]}</h3>' if t == "h3" else f'<h4 id="{esc(hid)}">{b["h"]}</h4>')
        elif t == "h2":
            out.append(f'<h3 id="{esc(b.get("id") or slugify(b["h"]))}">{b["h"]}</h3>')
        elif t in ("ul", "ol"):
            out.append(f"<{t}>" + "".join(f"<li>{i}</li>" for i in b["items"]) + f"</{t}>")
        elif t == "table":
            head = "".join(f"<th>{c}</th>" for c in b["head"])
            rows = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in b["rows"])
            out.append(f'<div class="ac-table"><table>{"<thead><tr>" + head + "</tr></thead>" if head else ""}<tbody>{rows}</tbody></table></div>')
        elif t == "pre":
            out.append(f'<pre class="ac-pre">{b["h"]}</pre>')
        elif t == "quote":
            out.append(f"<blockquote>{render_blocks(b['blocks'])}</blockquote>")
        elif t == "callout":
            k = b["kind"]
            body = render_blocks(b["blocks"])
            label = b["label"] or {"note": "Note"}.get(k, "Note")
            if k == "deeper":
                lab = re.sub(r"\s*\(optional\)\s*$", "", label, flags=re.I)
                lab = re.sub(r"^Go deeper:\s*", "", lab)
                lab = lab[:1].upper() + lab[1:]
                out.append(f'<details class="ac-co ac-co-deeper"><summary><span class="ac-co-ic">{{{{icon:layers}}}}</span>'
                           f'<span class="ac-co-lab"><span class="ac-co-k">Go deeper</span>{lab}</span>'
                           f'<span class="ac-co-opt">Optional</span><span class="ac-co-chev">{{{{icon:chevron-down}}}}</span></summary>'
                           f'<div class="ac-co-body">{body}</div></details>')
            elif k == "academy":
                out.append(f'<aside class="ac-co ac-co-academy"><p class="ac-co-lab"><span class="ac-co-ic">{{{{icon:book-open}}}}</span>{label}</p>'
                           f'<div class="ac-co-body">{body}<p><a class="ac-co-link" href="{SIGNUP}">Ask about team training {{{{icon:arrow-right}}}}</a></p></div></aside>')
            else:
                out.append(f'<aside class="ac-co ac-co-{k}"><p class="ac-co-lab"><span class="ac-co-ic">{{{{icon:{ICON.get(k, "message")}}}}}</span>{label}</p>'
                           f'<div class="ac-co-body">{body}</div></aside>')
    return "\n".join(out)


def link_guides(h, self_slug):
    for slug, label, *_ in DESK:
        title = "AI for " + {"ai-for-hedge-funds": "Hedge Funds", "ai-for-asset-management": "Asset Management",
                             "ai-for-investment-banking": "Investment Banking", "ai-for-private-equity": "Private Equity"}[slug]
        if slug != self_slug and title in h and f'href="/guides/{slug}"' not in h:
            h = h.replace(title, f'<a href="/guides/{slug}">{title}</a>', 1)
    return h



# ---------------------------------------------------------------- v2: site visual language
# Dark teal hero (hero-teal hero-ent, as /platform), a dark band carrying a white card (as the platform
# architecture card), mono green eyebrows, two-tone headlines, mint and cream panels, cream FAQ, dark demo band.
def I(name):
    return "{{icon:" + name + "}}"


ARROW = I("arrow-right")
DESK_ICON = {"ai-for-hedge-funds": "trending-up", "ai-for-asset-management": "pie-chart",
             "ai-for-investment-banking": "landmark", "ai-for-private-equity": "briefcase"}
FUND_ICON = {"large-language-models": "brain", "prompt-engineering": "edit", "rag-retrieval-augmented-generation": "file-search",
             "ai-agents": "bot", "context-windows": "scan-text", "knowledge-graphs": "network", "ai-hallucinations": "alert",
             "reasoning-models": "git-branch", "embeddings": "layers", "model-context-protocol": "plug"}
LIB_ICON = {"/pascal-academy/ai-glossary": "book-open", "/pascal-academy/workflows": "workflow",
            "/pascal-academy/prompt-library": "message", "/pascal-academy/agent-library": "bot"}
SCRIPT = '<script src="/assets/pages/academy.js" defer></script>\n'


def hero(eyebrow, h1, lead, actions="", extra="", cls=""):
    return f"""<section class="hero-teal hero-ent ac-hero{(" " + cls) if cls else ""}" aria-labelledby="page-title">
  <div class="hero-teal-in">
    {{{{crumbs}}}}
    <div class="ht-grid">
      <div><h1 class="h1" id="page-title"><span class="h1-k"><span class="eyebrow">{eyebrow}</span></span>{h1}</h1></div>
      <div class="ht-side">
        <p class="lead">{lead}</p>
        {f'<div class="actions">{actions}</div>' if actions else ""}
        {extra}
      </div>
    </div>
  </div>
</section>
"""


def band(inner, cls=""):
    return f"""<section class="arch-band arch-band-join ac-band{(" " + cls) if cls else ""}">
  <div class="frame">
    {inner}
  </div>
</section>
"""


def sec_head(n, eyebrow, h2, sub="", hid=None, right=""):
    hid = hid or slugify(eyebrow) + "-h"
    return f"""<div class="ac-head">
      <div><p class="eyebrow">{n} {eyebrow}</p>
      <h2 class="h2" id="{hid}">{h2}{f' <span class="mute">{sub}</span>' if sub else ""}</h2></div>
      {right}
    </div>"""


def workshop():
    return f"""<section class="ac-ws" aria-labelledby="ws-title">
  <div class="frame">
    <div class="ac-ws-in">
      <div>
        <p class="eyebrow">Workshops</p>
        <h2 class="h2" id="ws-title">Join Pascal Academy. <span class="mute">Learn directly from the Pascal team through live workshops.</span></h2>
      </div>
      <a class="btn btn-white" href="{SIGNUP}">Sign up {ARROW}</a>
    </div>
  </div>
</section>
"""


DEMO = '<!--#include demo-band title="Ask your first question with your firm\'s context." sub="A walkthrough with your own documents connected."-->\n'


def faq_block(faqs, title_id="faq-title"):
    items = "".join(f'<details class="faq-item"><summary>{q}<span class="pm" aria-hidden="true"></span></summary>'
                    f'<div class="ans">{a}</div></details>\n' for q, a in faqs)
    return f"""<section class="row row-pad bg-cream" id="faq" aria-labelledby="{title_id}">
    <div class="faq-wrap">
      <div><h2 class="h2" id="{title_id}">Frequently asked questions</h2></div>
      <div class="faq">
{items}      </div>
    </div>
  </section>
"""


def shot(img, lazy=True):
    f, w, h, alt = img
    return (f'<div class="shot"><img src="/assets/shots/{f}" alt="{esc(alt)}" width="{w}" height="{h}"'
            f'{LAZY if lazy else ""} decoding="async"></div>')


def ico(name, cls="ac-ic"):
    return f'<span class="{cls}">{I(name)}</span>'


def two_tone(title, rest):
    return f'{title} <span class="mute">{rest}</span>'


# ---------------------------------------------------------------- PDF gate
def gate(title, slug, mins_read):
    return f"""<dialog class="ac-gate" id="pdf-gate" aria-labelledby="gate-h">
  <div class="ac-gate-in">
    <div class="ac-gate-side">
      <p class="eyebrow">Pascal Academy · PDF</p>
      <p class="ac-gate-t">{title}</p>
      <p class="ac-gate-m">{mins_read} min read</p>
      <div class="ac-gate-doc" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><b></b><i></i><i></i></div>
    </div>
    <div class="ac-gate-main">
      <button class="ac-gate-x" type="button" data-gate-close aria-label="Close">{I("close")}</button>
      <form class="ac-gate-form" data-gate-form data-guide="{esc(title)}" data-slug="{slug}" data-pdf="/assets/academy/pdf/{slug}.pdf" novalidate>
        <h2 id="gate-h">Get this guide as a PDF</h2>
        <p class="ac-gate-sub">Tell us where to send it and we will email you the PDF.</p>
        <label>Full name<input name="name" autocomplete="name" required></label>
        <label>Work email<input name="email" type="email" autocomplete="email" required></label>
        <label>Organization<input name="organization" autocomplete="organization" required></label>
        <p class="ac-gate-err" role="alert" hidden></p>
        <button class="btn btn-dark" type="submit">Email me the PDF {ARROW}</button>
        <p class="ac-gate-fine">By submitting, you agree to be contacted about Pascal Academy.</p>
      </form>
      <div class="ac-gate-done" hidden>
        <span class="ac-gate-ok">{I("check")}</span>
        <h2>Check your inbox.</h2>
        <p>We have sent <b>{title}</b> to <span data-gate-email></span>.</p>
        <button class="btn btn-line" type="button" data-gate-close>Back to the guide</button>
      </div>
    </div>
  </div>
</dialog>
"""


# ---------------------------------------------------------------- docs
def doc_page(slug):
    d = load(slug)
    desk = d["kind"] == "desk"
    m = mins(d["meta"])
    if desk:
        idx = [s for s, *_ in DESK].index(slug)
        _, label, hubdesc, img, panel = DESK[idx]
        seq = [(f"/guides/{s}", "AI for " + l.lower(), s) for s, l, *_ in DESK]
        crumbs = [["Pascal Academy", HUB], ["Desk guides", HUB + "#guides"], [d["title"], d["path"]]]
        eyebrow = f"Desk guide · {label}"
        h1 = two_tone("AI for", label.lower() + ".")
    else:
        idx = [s for s, *_ in FUND].index(slug)
        seq = [(f"/pascal-academy/guides/{s}", l, s) for s, l, _ in FUND]
        crumbs = [["Pascal Academy", HUB], ["AI fundamentals", "/pascal-academy/ai-fundamentals"], [d["title"], d["path"]]]
        eyebrow = f"AI fundamentals · Part {idx + 1} of {len(FUND)}"
        h1 = two_tone(d["title"], "explained.")
    parts = [p.strip().replace("~", "") for p in d["meta"].split("·") if p.strip() and p.strip() != "Pascal Academy"]
    updated = next((p for p in parts if p.startswith("Updated")), "")
    parts = [p for p in parts if not p.startswith("Updated")]
    upd = [b["h"] for b in d["about"] if b["t"] == "updated"]
    updated = updated or ("Updated " + upd[0] if upd else "")
    meta_items = parts + ([updated] if updated else [])
    meta_html = "".join(f"<span>{esc(p)}</span>" for p in meta_items)

    chapters = d["chapters"]
    # band card: chapters (left) + series list or product shot (right)
    chips = "".join(f'<a class="ac-ch" href="#{esc(c["id"])}"><span>{i + 1:02d}</span>{re.sub(r"<[^>]+>", "", c["h"])}</a>'
                    for i, c in enumerate(chapters))
    if desk:
        right = f'<div class="ac-card-media"><div class="panel {panel}">{shot(img, lazy=False)}</div></div>'
    else:
        series = "".join(f'<li><a href="{h}"{CUR if s == slug else ""}><span>{i + 1:02d}</span>{esc(l)}</a></li>'
                         for i, (h, l, s) in enumerate(seq))
        right = f'<div class="ac-card-series"><p class="ac-card-k">The AI fundamentals series</p><ol>{series}</ol></div>'
    card = f"""<div class="ac-card ac-card-doc">
      <div class="ac-card-main">
        <div class="ac-card-top"><p class="ac-card-k">In this guide</p>
          <div class="ac-card-meta"><span class="ac-by">{ico("book-open", "ac-by-mark")}Pascal Academy</span>{meta_html}</div></div>
        <nav class="ac-chs" aria-label="Chapters">{chips}</nav>
        <div class="ac-card-actions">
          <button class="btn btn-dark btn-sm" type="button" data-gate-open>{I("file-text")} Download the PDF</button>
          <a class="link" href="#{esc(chapters[0]["id"])}">Start reading {ARROW}</a>
        </div>
      </div>
      {right}
    </div>"""

    body = []
    if d["intro"]:
        body.append(f'<div class="ac-intro">{render_blocks(d["intro"])}</div>')
    for i, c in enumerate(chapters):
        bl = render_blocks(c["blocks"])
        if re.match(r"further reading", c["h"], re.I):
            bl = link_guides(bl, slug)
        body.append(f'<section class="ac-sec" id="{esc(c["id"])}" aria-labelledby="{esc(c["id"])}-h">'
                    f'<p class="ac-chap">Chapter {i + 1:02d}</p><h2 id="{esc(c["id"])}-h">{c["h"]}</h2>\n{bl}\n</section>')
    about = [b for b in d["about"] if b["t"] == "p"] + d["outro"]
    if about:
        body.append(f'<aside class="ac-about">{ico("book-open", "ac-about-mark")}<div><p class="ac-about-h">About this guide</p>{render_blocks(about)}</div></aside>')
    toc = "".join(f'<li><a href="#{esc(c["id"])}">{re.sub(r"<[^>]+>", "", c["h"])}</a></li>' for c in chapters)
    if d["faqs"]:
        toc += '<li><a href="#faq">Frequently asked questions</a></li>'
    # keep learning: previous, next and the series/hub
    prev = seq[idx - 1] if idx > 0 else None
    nxt = seq[idx + 1] if idx + 1 < len(seq) else None
    kl = []
    if prev:
        kl.append(f'<a class="ac-kl" href="{prev[0]}"><span class="ac-kl-k">{I("arrow-left")} Previous</span><b>{esc(prev[1][:1].upper() + prev[1][1:])}</b></a>')
    if nxt:
        kl.append(f'<a class="ac-kl" href="{nxt[0]}"><span class="ac-kl-k">Next {ARROW}</span><b>{esc(nxt[1][:1].upper() + nxt[1][1:])}</b></a>')
    if desk:
        kl.append(f'<a class="ac-kl" href="/pascal-academy/ai-fundamentals"><span class="ac-kl-k">Series</span><b>AI fundamentals: 10 guides</b></a>')
    else:
        kl.append(f'<a class="ac-kl" href="/pascal-academy/ai-glossary"><span class="ac-kl-k">Reference</span><b>AI glossary for finance</b></a>')
    title, desc = SEO[slug]
    words = sum(len(re.sub(r"<[^>]+>", " ", x).split()) for x in body)
    meta = {"path": d["path"], "title": title, "description": desc, "crumbs": crumbs, "schema": "article",
            "name": d["title"], "og_kicker": "Pascal Academy", "og_title": d["title"] + (": " + d["dek"] if desk and len(d["dek"]) < 70 else ""),
            "llms": desc, "css": ["academy.css"], "word_limit": max(2000, words + 900),
            "faq_min": min(4, len(d["faqs"])), "lead_min": 8, "lead_max": 60, "priority": 0.7}
    return front(meta) + hero(eyebrow, h1, d["dek"], cls="ac-hero-doc") + band(card) + f"""<div class="ac ac-docpage">
<div class="frame">
  <div class="ac-docgrid">
    <aside class="ac-toc" aria-label="On this page">
      <div class="ac-toc-in">
        <p class="ac-toc-h">On this page</p>
        <ol data-spy>{toc}</ol>
        <div class="ac-toc-card">
          <p><b>Take it with you.</b> Get this guide as a PDF in your inbox.</p>
          <button class="btn btn-dark btn-sm" type="button" data-gate-open>{I("file-text")} Download the PDF</button>
        </div>
      </div>
    </aside>
    <article class="ac-prose" id="article">
      <details class="ac-toc-m"><summary>On this page {I("chevron-down")}</summary><ol>{toc}</ol></details>
{chr(10).join(body)}
    </article>
  </div>
  {faq_block(d["faqs"]) if d["faqs"] else ""}
  <section class="row ac-keep" aria-labelledby="keep-h">
    <h2 class="ac-keep-h" id="keep-h">Keep learning</h2>
    <div class="ac-kls">{"".join(kl)}</div>
  </section>
</div>
</div>
""" + workshop() + DEMO + gate(d["title"], slug, m) + SCRIPT


# ---------------------------------------------------------------- hub
def counts():
    g, w, p = load("lib-glossary"), load("lib-workflows"), load("lib-prompts")
    return {"terms": sum(len(x["terms"]) for x in g["groups"]), "themes": len(g["groups"]),
            "workflows": sum(len(c["items"]) for c in w["cats"]), "prompts": len(p["items"]),
            "fund_min": sum(mins(load(s)["meta"]) or 0 for s, *_ in FUND)}


def desk_card(i, h="h3"):
    slug, label, desc, img, panel = DESK[i]
    d = load(slug)
    return f"""<a class="ac-gcard" href="/guides/{slug}" data-item>
        <div class="panel {panel} ac-gcard-media">{shot(img)}</div>
        <div class="ac-gcard-copy">
          <p class="ac-gcard-meta">{ico(DESK_ICON[slug], "ac-ic ac-ic-sm")}Desk guide · {mins(d["meta"])} min read</p>
          <{h} class="ac-gcard-h">{d["title"]}</{h}><p>{desc}</p>
          <span class="link">Read the guide {ARROW}</span>
        </div>
      </a>"""


def fund_card(i, h="h3"):
    slug, label, desc = FUND[i]
    d = load(slug)
    return f"""<a class="ac-fcard" href="/pascal-academy/guides/{slug}" data-item>
        <span class="ac-fcard-top">{ico(FUND_ICON[slug])}<span class="ac-fcard-n">Part {i + 1:02d} · {mins(d["meta"])} min</span></span>
        <{h} class="ac-fcard-h">{esc(label)}</{h}>
        <span class="ac-fcard-d">{esc(desc)}</span>
      </a>"""


def hub_page():
    c = counts()
    lib_meta = {"/pascal-academy/ai-glossary": f"{c['terms']} terms · {c['themes']} themes",
                "/pascal-academy/workflows": f"{c['workflows']} workflows",
                "/pascal-academy/prompt-library": f"{c['prompts']} prompts",
                "/pascal-academy/agent-library": "3 agents · 6 templates"}
    ax_desk = "".join(f'<a class="ax-card" href="/guides/{s}">{ico(DESK_ICON[s], "ax-ic")}<b>AI for {l.lower()}</b>'
                      f'<span class="ax-sub">{mins(load(s)["meta"])} min read</span></a>' for s, l, *_ in DESK)
    ax_fund = "".join(f'<a class="ax-card ax-card-sm" href="/pascal-academy/guides/{s}">{ico(FUND_ICON[s], "ax-ic")}<b>{esc(l)}</b></a>' for s, l, _ in FUND)
    ax_lib = "".join(f'<a class="ax-card" href="{h}">{ico(LIB_ICON[h], "ax-ic")}<b>{esc(l)}</b><span class="ax-sub">{lib_meta[h]}</span></a>' for h, l, _ in LIB)
    card = f"""<figure class="ac-map" aria-label="Pascal Academy at a glance">
      <div class="ac-map-row"><p class="ax-k">Desk guides</p><div class="ac-g4">{ax_desk}</div></div>
      <div class="ac-map-row"><p class="ax-k">AI fundamentals</p><div class="ac-g5">{ax_fund}</div></div>
      <div class="ac-map-row"><p class="ax-k">Library</p><div class="ac-g4">{ax_lib}</div></div>
    </figure>"""
    lib_cells = "".join(f"""<a class="cell ac-cell" href="{h}" data-item>{ico(LIB_ICON[h], "ac-ic")}<b>{esc(l)}</b>
        <span>{esc(d)}</span><span class="ac-cell-meta">{lib_meta[h]}</span><span class="link">Open {esc(l[:1].lower() + l[1:]) if l != "AI glossary" else "the AI glossary"} {ARROW}</span></a>""" for h, l, d in LIB)
    meta = {"path": HUB, "title": "Pascal Academy: Learn AI for Institutional Finance",
            "description": "Practical AI education for investment teams: desk guides, AI fundamentals, a finance AI glossary, workflows, prompts and agents, plus live workshops.",
            "crumbs": [["Pascal Academy", HUB]], "og_kicker": "Pascal Academy", "og_title": "Learn AI for institutional finance",
            "llms": "Pascal Academy home: desk guides for hedge funds, asset managers, investment banks and private equity, a ten-part AI fundamentals series, an AI glossary for finance, workflows, prompts and agents.",
            "css": ["academy.css"], "word_limit": 1300, "faq_min": 0, "priority": 0.8}
    search = (f'<label class="ac-search ac-search-dark"><span class="sr-only">Search Pascal Academy</span>{I("search")}'
              f'<input type="search" placeholder="Search guides, concepts and tools" data-filter="#hub-results" autocomplete="off"></label>')
    return front(meta) + hero(
        "Pascal Academy", two_tone("Learn AI for", "institutional finance."),
        "Pascal Academy is practical AI education for modern investment teams: guides for every desk, the core concepts explained simply, and tested workflows, prompts and agents.",
        actions=f'<a class="btn btn-white" href="#guides">Start learning</a><a class="btn btn-line" href="{SIGNUP}">Join a workshop</a>') + band(card) + f"""<div class="ac ac-hub">
<div class="frame">
  <section class="cells c4 ac-stats" aria-label="Pascal Academy in numbers">
    <div class="cell"><span class="stat-num">{len(DESK) + len(FUND)}</span><span class="stat-lbl">Guides across desks and AI concepts</span></div>
    <div class="cell"><span class="stat-num">{c["terms"]}</span><span class="stat-lbl">AI terms defined for finance</span></div>
    <div class="cell"><span class="stat-num">{c["workflows"]}</span><span class="stat-lbl">Step-by-step workflows</span></div>
    <div class="cell"><span class="stat-num">{c["prompts"]}</span><span class="stat-lbl">Tested prompts, ready to copy</span></div>
  </section>
  <div class="row ac-searchrow">{search}<p class="ac-empty" hidden>Nothing matches that search. Try a broader term.</p></div>
  <div id="hub-results">
  <section class="row row-pad" id="guides" aria-labelledby="guides-h" data-group>
    {sec_head("01", "Desk guides", "Guides for every investment desk.", "Practical playbooks for hedge funds, asset managers, bankers, and private markets teams.", "guides-h")}
    <div class="ac-gcards">{"".join(desk_card(i) for i in range(len(DESK)))}</div>
  </section>
  <section class="row row-pad bg-mint" id="fundamentals" aria-labelledby="fund-h" data-group>
    {sec_head("02", "AI fundamentals", "Build the vocabulary.", "The core concepts behind AI, explained simply.", "fund-h",
              f'<a class="btn btn-dark btn-sm" href="/pascal-academy/ai-fundamentals">See the series {ARROW}</a>')}
    <div class="ac-fcards">{"".join(fund_card(i) for i in range(len(FUND)))}</div>
  </section>
  <section class="row" id="library" aria-labelledby="lib-h" data-group>
    <div class="row-pad-sm ac-libhead">{sec_head("03", "Library", "A growing library of AI resources.", "Concepts, workflows, and reference material for institutional teams.", "lib-h")}</div>
    <div class="cells c4 row ac-libcells">{lib_cells}</div>
  </section>
  </div>
</div>
</div>
""" + workshop() + DEMO + SCRIPT


# ---------------------------------------------------------------- AI fundamentals index
def fund_index():
    c = counts()
    meta = {"path": "/pascal-academy/ai-fundamentals", "title": "AI Fundamentals for Finance | Pascal Academy",
            "description": "Build a practical understanding of modern AI concepts and how they apply to institutional finance, from LLMs and RAG to agents, embeddings and MCP.",
            "crumbs": [["Pascal Academy", HUB], ["AI fundamentals", "/pascal-academy/ai-fundamentals"]],
            "og_kicker": "Pascal Academy", "og_title": "AI fundamentals for institutional finance",
            "llms": "Index of the ten-part AI Fundamentals series: LLMs, prompt engineering, RAG, AI agents, context windows, knowledge graphs, hallucinations, reasoning models, embeddings and MCP.",
            "css": ["academy.css"], "word_limit": 1000, "faq_min": 0, "priority": 0.7}
    rows = "".join(f"""<a class="ac-srow" href="/pascal-academy/guides/{s}">
        <span class="ac-srow-n">{i + 1:02d}</span>{ico(FUND_ICON[s])}
        <span class="ac-srow-copy"><h3>{esc(l)}</h3><span>{esc(desc)}</span></span>
        <span class="ac-srow-m">{mins(load(s)["meta"])} min</span><span class="ac-srow-a">{ARROW}</span></a>""" for i, (s, l, desc) in enumerate(FUND))
    more = [("/pascal-academy/workflows", "Workflows", "How AI is applied across research, due diligence, modelling and investment workflows."),
            ("/pascal-academy/prompt-library", "Prompt library", "Browse tested prompts for institutional finance."),
            ("/pascal-academy/ai-glossary", "AI glossary", "Explore AI terminology through an A-Z reference.")]
    more_cells = "".join(f"""<a class="cell ac-cell" href="{h}">{ico(LIB_ICON[h], "ac-ic")}<b>{l}</b><span>{esc(d)}</span>
        <span class="link">Open {l[:1].lower() + l[1:] if l != "AI glossary" else "the AI glossary"} {ARROW}</span></a>""" for h, l, d in more)
    stats = (f'<div class="ac-hstats"><span><b>{len(FUND)}</b> guides</span><span><b>{c["fund_min"]}</b> min in total</span>'
             f'<span>Beginner-friendly with advanced sections</span></div>')
    return front(meta) + hero("AI fundamentals", two_tone("AI fundamentals", "for institutional finance."),
                              "Build a practical understanding of modern AI concepts and learn how they apply to institutional finance.",
                              actions=f'<a class="btn btn-white" href="/pascal-academy/guides/{FUND[0][0]}">Start with part 1</a>',
                              extra=stats) + band(f'<div class="ac-card ac-card-list"><div class="ac-card-top"><h2 class="ac-card-k">Build the vocabulary</h2></div><p class="ac-card-lead">Short explainers for the ideas that keep showing up in institutional AI work.</p>{rows}</div>') + f"""<div class="ac">
<div class="frame">
  <section class="row" aria-labelledby="more-h">
    <div class="row-pad-sm">{sec_head("", "Keep going", "More from Pascal Academy.", "", "more-h")}</div>
    <div class="cells row">{more_cells}</div>
  </section>
</div>
</div>
""" + workshop() + DEMO + SCRIPT


# ---------------------------------------------------------------- library shell
def search_box(target, placeholder, dark=False):
    return (f'<label class="ac-search{" ac-search-dark" if dark else ""}"><span class="sr-only">{esc(placeholder)}</span>{I("search")}'
            f'<input type="search" placeholder="{esc(placeholder)}" data-filter="{target}" autocomplete="off"></label>')


def cats_nav(label, items):
    lis = "".join(f'<li><a href="#{slugify(n)}">{esc(n)}<span>{k}</span></a></li>' for n, k in items)
    return f'<nav class="ac-cats" aria-label="{label}"><p class="ac-cats-h">{label}</p><ol data-spy>{lis}</ol></nav>'


def glossary_page():
    g = load("lib-glossary")
    n = sum(len(x["terms"]) for x in g["groups"])
    gicon = ["brain", "bot", "file-search", "edit", "plug", "shield-check"]
    groups = []
    for gi, x in enumerate(g["groups"]):
        terms = "".join(f"""<div class="ac-term" id="{slugify(t["term"])}" data-item>
            <div class="ac-term-k"><h4>{t["term"]}</h4><span class="ac-tag">{esc(t["tag"].upper() if len(t["tag"]) <= 4 else t["tag"].title())}</span></div>
            <p>{t["def"]}</p></div>""" for t in x["terms"])
        groups.append(f"""<section class="ac-grp" id="{slugify(x["name"])}" aria-labelledby="{slugify(x["name"])}-h" data-group>
          <div class="ac-grp-head">{ico(gicon[gi % len(gicon)])}<div><h3 class="ac-grp-h" id="{slugify(x["name"])}-h">{x["name"]}</h3><p>{x["desc"]}</p></div><span class="ac-grp-n">{len(x["terms"])} terms</span></div>
          <div class="ac-terms">{terms}</div>
        </section>""")
    meta = {"path": "/pascal-academy/ai-glossary", "title": "AI Glossary for Finance | Pascal Academy",
            "description": "A finance-focused reference of AI terms for investment teams, covering LLMs, RAG, agents, embeddings, MCP and governance, grouped by theme with search.",
            "crumbs": [["Pascal Academy", HUB], ["AI glossary", "/pascal-academy/ai-glossary"]],
            "og_kicker": "Pascal Academy", "og_title": "AI glossary for finance",
            "llms": f"A finance-focused glossary of {n} AI terms for investment teams, grouped into themes: models and foundations, core AI and agents, retrieval and knowledge, prompting, integration and platform, finance and governance.",
            "css": ["academy.css"], "word_limit": 4300, "lead_min": 8, "priority": 0.7}
    themes = "".join(f'<a class="ax-card ax-card-sm" href="#{slugify(x["name"])}">{ico(gicon[i % len(gicon)], "ax-ic")}<b>{x["name"]}</b><span class="ax-sub">{len(x["terms"])} terms</span></a>' for i, x in enumerate(g["groups"]))
    return front(meta) + hero("AI glossary", two_tone("AI glossary", "for finance."),
                              "An A-to-Z reference of AI terms written for investment teams.",
                              extra=search_box("#gl-results", f"Search {n} terms", dark=True)) + band(
        f'<div class="ac-card ac-card-themes"><div class="ac-card-top"><p class="ac-card-k">Browse by theme</p><span class="ac-card-meta">{n} terms · {len(g["groups"])} themes</span></div><div class="ac-g3">{themes}</div></div>') + f"""<div class="ac ac-lib">
<div class="frame">
  <div class="row ac-libgrid" id="gl-results">
    <aside class="ac-side">{cats_nav("Themes", [(x["name"], len(x["terms"])) for x in g["groups"]])}</aside>
    <div class="ac-libmain">
      <div class="ac-libintro">{sec_head("", "AI terms for investment teams", "Browse the glossary.", "Finance-focused definitions grouped by theme.", "browse-h")}
        <p>Search or filter to find the terms that come up in research, modelling, and AI discussions. For the longer explanations, read the <a href="/pascal-academy/ai-fundamentals">AI fundamentals</a> series.</p></div>
      {"".join(groups)}
      <p class="ac-empty" hidden>No term matches that search.</p>
    </div>
  </div>
  {faq_block(g["faqs"])}
</div>
</div>
""" + workshop() + DEMO + SCRIPT


def workflows_page():
    w = load("lib-workflows")
    n = sum(len(c["items"]) for c in w["cats"])
    sicon = ["target", "folder-search", "workflow", "file-check", "eye"]
    stages = "".join(f"""<div class="ac-stage"><span class="ac-stage-n">{s["n"]}</span>{ico(sicon[i], "ax-ic")}<h3>{s["name"]}</h3>
        <p class="ac-stage-q">{s["q"]}</p><p>{s["d"]}</p></div>""" for i, s in enumerate(w["stages"]))
    groups = []
    for c in w["cats"]:
        items = []
        for it in c["items"]:
            steps = "".join(f"<li>{s}</li>" for s in it["steps"])
            flow = "".join(f"<li>{esc(f)}</li>" for f in it["flow"])
            inputs = "".join(f"<li>{i.strip()}</li>" for i in it["inputs"].split("·") if i.strip())
            items.append(f"""<details class="ac-wf" id="{esc(it["id"])}" data-item>
            <summary><span class="ac-wf-t"><h4>{it["title"]}</h4><span>{it["desc"]}</span></span><span class="ac-wf-chev">{I("plus")}</span></summary>
            <div class="ac-wf-body">
              <ol class="ac-flow" aria-label="Stages">{flow}</ol>
              <div class="ac-wf-cols">
                <div><p class="ac-wf-k">How it works</p><ol class="ac-steps">{steps}</ol></div>
                <div><p class="ac-wf-k">Inputs</p><ul class="ac-inputs">{inputs}</ul>
                  <p class="ac-wf-k">Output</p><p>{it["output"]}</p>
                  <p><a class="btn btn-dark btn-sm" href="{{{{demo_url}}}}">Try this workflow {ARROW}</a></p></div>
              </div>
            </div>
          </details>""")
        groups.append(f"""<section class="ac-grp" id="{slugify(c["name"])}" aria-labelledby="{slugify(c["name"])}-h" data-group>
          <div class="ac-grp-head"><div><h3 class="ac-grp-h" id="{slugify(c["name"])}-h">{c["name"]}</h3><p>{c["desc"]}</p></div><span class="ac-grp-n">{len(c["items"])} workflow{"s" if len(c["items"]) != 1 else ""}</span></div>
          <div class="ac-wfs">{"".join(items)}</div>
        </section>""")
    meta = {"path": "/pascal-academy/workflows", "title": "AI Workflows for Finance | Pascal Academy",
            "description": f"{n} step-by-step AI workflows for investment teams: earnings analysis, company research, peer comparison, bull and bear theses, news and events.",
            "crumbs": [["Pascal Academy", HUB], ["Workflows", "/pascal-academy/workflows"]],
            "og_kicker": "Pascal Academy", "og_title": "AI workflows for real financial work",
            "llms": f"{n} AI workflows for investment teams, each with its stages, inputs and output: earnings, company research, competition, news and events.",
            "css": ["academy.css"], "word_limit": 3300, "faq_min": 0, "priority": 0.7}
    anat = f"""<div class="ac-card ac-card-anat">
      <div class="ac-card-top"><h2 class="ac-card-k">The anatomy of a workflow</h2></div>
      <p class="ac-card-lead">Every workflow breaks a financial task into five stages: define the job, gather context, run the process, produce the deliverable, and review the result.</p>
      <div class="ac-stages">{stages}</div>
    </div>"""
    return front(meta) + hero("Workflows", two_tone("Workflows", "for real financial work."),
                              "How AI turns financial work into repeatable processes. See how real financial tasks can be broken down, automated, and run with AI.",
                              extra=search_box("#wf-results", f"Search {n} workflows", dark=True)) + band(anat) + f"""<div class="ac ac-lib">
<div class="frame">
  <div class="row ac-libgrid" id="wf-results">
    <aside class="ac-side">{cats_nav("Categories", [(c["name"], len(c["items"])) for c in w["cats"]])}</aside>
    <div class="ac-libmain">
      <div class="ac-libintro">{sec_head("", "The library", "Browse the library.", "Step-by-step workflows for the tasks analysts do every day.", "browse-h")}
        <p>Each one shows the inputs, process, and deliverable. Open a workflow to see how it runs, or use ready-made <a href="/pascal-academy/prompt-library">prompts</a> and <a href="/pascal-academy/agent-library">agents</a> for the same tasks.</p></div>
      {"".join(groups)}
      <p class="ac-empty" hidden>No workflow matches that search.</p>
    </div>
  </div>
</div>
</div>
""" + workshop() + DEMO + SCRIPT


def prompts_page():
    p = load("lib-prompts")
    cats = []
    for it in p["items"]:
        if it["cat"] not in cats:
            cats.append(it["cat"])
    groups = []
    for c in cats:
        cards = "".join(f"""<article class="ac-prompt" id="{slugify(it["title"])}" data-item>
            <div class="ac-prompt-head"><span class="ac-prompt-n">{it["n"]}</span><div><h4>{it["title"]}</h4><p class="ac-prompt-when">{it["when"]}</p></div></div>
            <div class="ac-prompt-box"><div class="ac-prompt-bar"><span><i></i><i></i><i></i></span><span>Prompt</span>
              <button type="button" class="ac-copy" data-copy>{I("file-text")}<span>Copy prompt</span></button></div><pre>{it["prompt"]}</pre></div>
          </article>""" for it in p["items"] if it["cat"] == c)
        groups.append(f"""<section class="ac-grp" id="{slugify(c)}" aria-labelledby="{slugify(c)}-h" data-group>
          <div class="ac-grp-head"><div><h3 class="ac-grp-h" id="{slugify(c)}-h">{esc(c)}</h3></div><span class="ac-grp-n">{sum(1 for i in p["items"] if i["cat"] == c)} prompts</span></div>
          <div class="ac-prompts">{cards}</div>
        </section>""")
    comps = "".join(f'<div class="ac-comp"><b>{x["k"]}</b><span>{x["v"]}</span></div>' for x in p["components"])
    mistakes = [m for m in p["mistakes"] if not m["k"].lower().startswith("chain")]
    cot = next((m for m in p["mistakes"] if m["k"].lower().startswith("chain")), None)
    mis = "".join(f'<div class="cell ac-cell">{ico("alert", "ac-ic")}<b>{m["k"]}</b><span>{m["v"]}</span></div>' for m in mistakes)
    bicon = ["scale", "gavel", "lock", "shield"]
    bounds = "".join(f'<div class="cell ac-cell">{ico(bicon[i], "ac-ic")}<b>{m["k"]}</b><span>{m["v"]}</span></div>' for i, m in enumerate(p["bounds"]))
    cot_html = (f'<aside class="ac-co ac-co-principle"><p class="ac-co-lab"><span class="ac-co-ic">{I("zap")}</span>{cot["k"]}</p>'
                f'<div class="ac-co-body"><p>{cot["v"]}</p></div></aside>') if cot else ""
    meta = {"path": "/pascal-academy/prompt-library", "title": "AI Prompts for Finance | Pascal Academy",
            "description": f"{len(p['items'])} tested AI prompts for institutional finance: company research, earnings, modelling, comps, IC memos, portfolio and investor communication.",
            "crumbs": [["Pascal Academy", HUB], ["Prompt library", "/pascal-academy/prompt-library"]],
            "og_kicker": "Pascal Academy", "og_title": "Tested AI prompts for finance",
            "llms": f"{len(p['items'])} copy-ready AI prompts for investment teams, plus how to structure a finance prompt and when AI should not make the call.",
            "css": ["academy.css"], "word_limit": 3500, "lead_min": 10, "priority": 0.7}
    howto = f"""<div class="ac-card ac-card-howto">
      <div><p class="ac-card-k">How to use this library</p><p class="ac-howto-h">Start with the task.</p>
      <p>Each card contains a structured prompt you can copy and adapt to your workflow. Replace the bracketed fields with your company, data and specific requirements. Add the context the model needs, then specify the format you want in the output.</p></div>
      <div class="ac-comps"><p class="ac-card-k">What a finance prompt contains</p>{comps}</div>
    </div>"""
    return front(meta) + hero("Prompt library", two_tone("AI prompts", "for finance."),
                              "Tested prompts for research, memos and modelling. Copy, adapt and run.",
                              extra=search_box("#pr-results", f"Search {len(p['items'])} prompts", dark=True)) + band(howto) + f"""<div class="ac ac-lib">
<div class="frame">
  <div class="row ac-libgrid" id="pr-results">
    <aside class="ac-side">{cats_nav("Categories", [(c, sum(1 for i in p["items"] if i["cat"] == c)) for c in cats])}</aside>
    <div class="ac-libmain">
      <div class="ac-libintro">{sec_head("", "Prompt library", "Browse tested prompts.", "Filter by category or search by task.", "browse-h")}
        <p>Each card includes a structured prompt you can copy and adapt for your workflow. The <a href="/pascal-academy/guides/prompt-engineering">prompt engineering guide</a> explains why these patterns work.</p></div>
      {"".join(groups)}
      <p class="ac-empty" hidden>No prompt matches that search.</p>
    </div>
  </div>
  <section class="row" aria-labelledby="better-h">
    <div class="row-pad-sm">{sec_head("", "Writing better prompts", "What makes a finance prompt effective.", "Output quality reflects input quality.", "better-h")}
      <p class="ac-headp">A prompt that produces a useful result for an investment task has a recognizable structure. These are the common mistakes to avoid.</p></div>
    <div class="cells c4 row">{mis}</div>
    <div class="row-pad-sm ac-cot">{cot_html}</div>
  </section>
  <section class="row bg-mint" aria-labelledby="bounds-h">
    <div class="row-pad-sm">{sec_head("", "Boundaries", "When AI should not make the call.", "Investment judgment stays with the analyst.", "bounds-h")}
      <p class="ac-headp">AI accelerates the analytical process, but investment judgment stays with the analyst. There are specific scenarios where AI should not be relied on for final outputs or decisions.</p></div>
    <div class="cells c4 row ac-cells-white">{bounds}</div>
  </section>
  {faq_block(p["faqs"])}
</div>
</div>
""" + workshop() + DEMO + SCRIPT


def agents_page():
    src = (ROOT.parent.parent / "_academy_src/txt/pascal-academy_agent-library.txt").read_text()
    lines = src.splitlines()
    ans = [l[4:] for l in lines[lines.index("[h2] Frequently asked questions."):] if l.startswith("[p] ")]
    faqs = list(zip(load_agent_faq_questions(), ans))
    agents = [
        ("Analysis", "01", "Generative Matrix", "table",
         "Filter companies, then analyze them using AI to answer your specific questions and get detailed insights across your filtered company set.",
         ["Select companies", "Define question", "Analyze", "Compare"], "Works with", ["Public companies", "Smart Search", "My Vault"],
         ("shot-agent-table.webp", 1600, 844, "Generative Matrix style output: a comparison table across companies with citations"), "panel-dark"),
        ("Extraction", "02", "KPI Extractor", "bar-chart",
         "Automatically extract tables and graphs from company filings and your own documents into Excel. No more manual copy-paste.",
         ["Select company", "Select source", "Select period", "Extract"], "Sources", ["Annual Report", "Earnings Presentation", "Quarterly Report", "My Vault"],
         ("shot-excel.webp", 1600, 504, "Excel model with the Pascal KPI Extractor panel planning its steps"), "panel-cream"),
        ("Generation", "03", "Research Memo Generator", "file-text",
         "Generate customized company research reports using your fund's template. No more hours of research, just a click.",
         ["Select sources", "Choose template", "Generate", "Review"], "Templates", ["Company Primer", "Earnings Analysis", "IPO Prospectus", "Credit Memo", "+ Custom"],
         ("shot-word.webp", 1316, 660, "Word research memo generated by Pascal from a template"), "panel-dark"),
    ]
    rows = []
    for i, (cat, n, name, icon, desc, steps, klab, kv, img, panel) in enumerate(agents):
        st = "".join(f"<li>{esc(s)}</li>" for s in steps)
        kvs = "".join(f"<li>{esc(x)}</li>" for x in kv)
        rows.append(f"""<section class="row split{" flip" if i % 2 else ""} ac-agent" id="{slugify(name)}" aria-labelledby="{slugify(name)}-h">
    <div class="split-copy">
      <p class="eyebrow">{n} {cat}</p>
      <h3 class="h2" id="{slugify(name)}-h">{name}.</h3>
      <p>{esc(desc)}</p>
      <ol class="ac-flow">{st}</ol>
      <p class="ac-wf-k">{klab}</p><ul class="ac-inputs">{kvs}</ul>
      <a class="link" href="{{{{demo_url}}}}">Run agent {ARROW}</a>
    </div>
    <div class="split-media"><div class="panel {panel}">{shot(img)}</div></div>
  </section>""")
    why = [("layers", "Built for investment work", "Each agent is designed around a defined investment workflow, from screening and extraction to memo generation and portfolio monitoring."),
           ("settings", "Simple setup", "Select the companies, sources, and output format you need. The agent applies the workflow and produces a structured result."),
           ("quote", "Source-backed outputs", "Every output includes citations to the underlying sources, making facts, figures, and conclusions easy to trace and verify.")]
    how = [("01", "Select your inputs", "Choose companies, filings, documents, or your own uploaded research. The agent works with public filings and your internal files side by side."),
           ("02", "Define what you need", "Pick a template, specify a question, or select which KPIs to extract. The agent's guided setup walks you through the options."),
           ("03", "Get a cited output", "The agent processes the inputs and returns a structured result. Every number, claim, and data point traces back to the source line it came from.")]
    tpl = [("01", "Company Primer", "A structured one-page overview of any public company. Business model, revenue segments, competitive position, key financials.", "/pascal-academy/workflows#company-primer"),
           ("02", "Earnings Analysis", "From earnings release to structured analysis. KPIs, guidance changes, management commentary, and estimate revisions.", "/pascal-academy/workflows#earnings-summary"),
           ("03", "IPO Prospectus", "Summarize and structure an IPO prospectus. Business overview, use of proceeds, risk factors, and financial highlights.", "/pascal-academy/workflows#ipo-prospectus"),
           ("04", "Annual Report Summariser", "Turn a full annual report into a structured summary. MD&A, financial statements, segment performance, and forward-looking commentary.", "/pascal-academy/workflows#annual-report"),
           ("05", "Credit Memo", "Generate a credit memo from financial data and filings. Credit metrics, covenant analysis, repayment capacity, and risk assessment.", "{{demo_url}}"),
           ("+", "Create Custom Template", "Start from scratch. Define your own sections, data points, and structure in the template builder.", "{{demo_url}}")]
    own = [("1", "Task", "What needs to get done?"), ("2", "Inputs", "What companies, filings, or documents does it need?"),
           ("3", "Process", "What should it do with those inputs?"), ("4", "Output", "What should the finished result look like?"),
           ("5", "Review", "How will you verify the result is accurate?")]
    why_cells = "".join(f'<div class="cell ac-cell">{ico(a, "ac-ic")}<b>{b}</b><span>{esc(c)}</span></div>' for a, b, c in why)
    how_cells = "".join(f'<div class="cell ac-cell"><span class="n">Step {a}</span><b>{b}</b><span>{esc(c)}</span></div>' for a, b, c in how)
    tpls = "".join(f'<a class="cell ac-cell" href="{h}"><span class="n">{a}</span><b>{b}</b><span>{esc(c)}</span><span class="link">{"Open the workflow" if h.startswith("/") else "See it in a demo"} {ARROW}</span></a>' for a, b, c, h in tpl)
    own_cells = "".join(f'<div class="ac-own"><span class="ac-own-n">{a}</span><b>{b}</b><span>{esc(c)}</span></div>' for a, b, c in own)
    meta = {"path": "/pascal-academy/agent-library", "title": "AI Agents for Finance | Pascal Academy",
            "description": "Pascal's AI agents for institutional finance: screen company universes, extract KPIs from filings into Excel, and generate research memos from templates.",
            "crumbs": [["Pascal Academy", HUB], ["Agent library", "/pascal-academy/agent-library"]],
            "og_kicker": "Pascal Academy", "og_title": "AI agents for investment research",
            "llms": "Pascal's agent library: Generative Matrix (screen and analyse companies), KPI Extractor (filings to Excel), Research Memo Generator (template reports), with research templates and a framework for building your own agent.",
            "css": ["academy.css"], "word_limit": 1600, "lead_min": 8, "priority": 0.7}
    ax = "".join(f'<a class="ax-card" href="#{slugify(a[2])}">{ico(a[3], "ax-ic")}<b>{a[2]}</b><span class="ax-sub">{a[0]}</span></a>' for a in agents)
    return front(meta) + hero("Agent library", two_tone("AI agents", "for finance."),
                              "Purpose-built agents for institutional finance. Research, extract and generate.",
                              actions=f'<a class="btn btn-white" href="#agents">Explore agents</a><a class="btn btn-line" href="{SIGNUP}">Sign up</a>') + band(
        f'<div class="ac-card"><div class="ac-card-top"><p class="ac-card-k">Agents built around how investment teams actually work</p></div><div class="ac-g3">{ax}</div></div>') + f"""<div class="ac ac-lib">
<div class="frame">
  <section class="cells" aria-label="Why Pascal agents">{why_cells}</section>
  <section class="row row-pad-sm ac-agentshead" id="agents" aria-labelledby="all-h">
    {sec_head("", "All agents", "Agents for investment research.", "Each agent handles a specific task and delivers a structured output.", "all-h")}
    <p class="ac-headp">Run repeatable finance workflows, from research to memo generation. For the concepts behind them, read <a href="/pascal-academy/guides/ai-agents">AI agents explained</a>.</p>
  </section>
  {"".join(rows)}
  <section class="row bg-mint" aria-labelledby="how-h">
    <div class="row-pad-sm">{sec_head("", "How it works", "Build for the task.", "You define it, the agent runs it, you get a cited output.", "how-h")}
      <p class="ac-headp">Every Pascal agent follows the same pattern. You define what you need, the agent gathers and processes the inputs, and you get a structured output with citations back to the source.</p></div>
    <div class="cells row ac-cells-white">{how_cells}</div>
  </section>
  <section class="row" aria-labelledby="tpl-h">
    <div class="row-pad-sm">{sec_head("", "Research templates", "Pre-built templates for common research outputs.", "", "tpl-h")}
      <p class="ac-headp">The Research Memo Generator comes with templates designed for the outputs investment teams produce regularly. Each defines the structure, sections, and data points the agent should populate. You can also build your own from scratch.</p></div>
    <div class="cells row ac-cells-3x2">{tpls}</div>
  </section>
  <section class="row row-pad-sm ac-ownrow" aria-labelledby="own-h">
    {sec_head("", "Build your own", "Create an agent for your workflow.", "", "own-h")}
    <p class="ac-headp">The agents above cover common tasks, but every investment team has workflows specific to how they work. Start with a task you repeat every week and turn it into a reusable agent. The <a href="/pascal-academy/workflows">workflow library</a> shows the same five stages applied to real tasks.</p>
    <div class="ac-owns">{own_cells}</div>
  </section>
  {faq_block(faqs)}
</div>
</div>
""" + workshop() + DEMO + SCRIPT


def load_agent_faq_questions():
    from bs4 import BeautifulSoup
    s = BeautifulSoup((ROOT.parent.parent / "_academy_src/pascal-academy_agent-library.html").read_text(), "html.parser")
    out = []
    for b in s.find("main").find_all("button", attrs={"aria-expanded": True}):
        q = " ".join(b.get_text(" ").replace("+", " ").split())
        if q.endswith("?"):
            out.append(esc(q).replace("&#x27;", "'"))
    return out


# ---------------------------------------------------------------- workshop sign-up (replaces the live Next.js form)
def signup_page():
    meta = {"path": SIGNUP, "title": "Join Pascal Academy: Team AI Workshops",
            "description": "Sign up for Pascal Academy workshops. Train your investment team on practical AI workflows, planned around your firm by the Pascal team.",
            "crumbs": [["Pascal Academy", HUB], ["Sign up", SIGNUP]], "og_kicker": "Pascal Academy",
            "og_title": "Train your team with Pascal Academy", "llms": "Sign-up form for Pascal Academy team workshops.",
            "css": ["academy.css"], "word_limit": 700, "faq_min": 0, "lead_min": 10, "priority": 0.5}
    opts = lambda xs: '<option value="">Select…</option>' + "".join(f"<option>{x}</option>" for x in xs)
    codes = [("+1", "United States"), ("+44", "United Kingdom"), ("+91", "India"), ("+65", "Singapore"), ("+971", "United Arab Emirates"),
             ("+852", "Hong Kong"), ("+61", "Australia"), ("+49", "Germany"), ("+33", "France"), ("+81", "Japan")]
    code_opts = "".join(f'<option value="{c}" data-country="{n}">{n} ({c})</option>' for c, n in codes)
    form = f"""<div class="ac-card ac-card-form">
      <div class="ac-form-side">
        <p class="ac-card-k">Tell us about your team</p>
        <p class="ac-howto-h">We'll follow up to plan a workshop tailored to your firm.</p>
        <ul class="ac-form-list">
          <li>{ico("book-open", "ax-ic")}<span><a href="{HUB}#guides"><b>Desk guides</b></a> for hedge funds, asset managers, bankers and private equity</span></li>
          <li>{ico("brain", "ax-ic")}<span><a href="/pascal-academy/ai-fundamentals"><b>AI fundamentals</b></a>, from LLMs and RAG to agents and MCP</span></li>
          <li>{ico("workflow", "ax-ic")}<span><a href="/pascal-academy/workflows"><b>Workflows</b></a>, <a href="/pascal-academy/prompt-library"><b>prompts</b></a> and <a href="/pascal-academy/agent-library"><b>agents</b></a> your team can run the next day</span></li>
        </ul>
        <a class="link" href="{HUB}">{I("arrow-left")} Back to Academy</a>
      </div>
      <form class="ac-form" data-signup-form novalidate>
        <label>Full name *<input name="name" autocomplete="name" required></label>
        <label>Work email *<input name="email" type="email" autocomplete="email" required></label>
        <label>Organization *<input name="organization" autocomplete="organization" required></label>
        <div class="ac-form-2">
          <label>Team size *<select name="teamSize" required>{opts(["1–5", "6–20", "21–50", "51–200", "200+"])}</select></label>
          <label>Focus area<select name="focus">{opts(["Hedge Funds", "Asset Management", "Investment Banking", "Private Equity", "Other"])}</select></label>
        </div>
        <label>Phone <span class="ac-opt">(optional)</span><span class="ac-phone"><select name="countryCode" aria-label="Country code">{code_opts}</select><input name="phone" type="tel" autocomplete="tel-national" inputmode="tel"></span></label>
        <p class="ac-gate-err" role="alert" hidden></p>
        <button class="btn btn-dark" type="submit">Sign up {ARROW}</button>
        <p class="ac-gate-fine">By submitting, you agree to be contacted about Pascal Academy.</p>
      </form>
      <div class="ac-gate-done ac-form-done" hidden>
        <span class="ac-gate-ok">{I("check")}</span>
        <h2>Thank you.</h2>
        <p>The Pascal team will reach out to plan a program for your organization.</p>
        <a class="btn btn-line" href="{HUB}">Back to Academy</a>
      </div>
    </div>"""
    return front(meta) + hero("Pascal Academy", two_tone("Train your team", "with Pascal Academy."),
                              "Learn how to apply AI across your team's day-to-day investment workflows.") + band(form, "ac-band-form") + DEMO + SCRIPT


# ---------------------------------------------------------------- main
def main():
    STAGING.mkdir(exist_ok=True)
    for f in STAGING.glob("*.html"):
        f.unlink()
    pages = {"academy-hub": hub_page(), "academy-fundamentals": fund_index(), "academy-glossary": glossary_page(),
             "academy-workflows": workflows_page(), "academy-prompts": prompts_page(), "academy-agents": agents_page(),
             "academy-signup": signup_page()}
    for s, *_ in DESK:
        pages[f"academy-guide-{s.removeprefix('ai-for-')}"] = doc_page(s)
    for s, *_ in FUND:
        pages[f"academy-fund-{s}"] = doc_page(s)
    for name, src in pages.items():
        (STAGING / f"{name}.html").write_text(src)
    print(f"{len(pages)} sources → {STAGING}")
    if "--promote" in sys.argv:
        for name in pages:
            shutil.copy(STAGING / f"{name}.html", PAGES / f"{name}.html")
        print(f"promoted to {PAGES}")
    print(",".join(pages))


if __name__ == "__main__":
    main()
