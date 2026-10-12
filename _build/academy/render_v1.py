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


# ---------------------------------------------------------------- shared chrome
def bar(active):
    items = [("Home", HUB, "hub"), ("Desk guides", HUB + "#guides", "desk"),
             ("AI fundamentals", "/pascal-academy/ai-fundamentals", "fund"),
             ("Glossary", "/pascal-academy/ai-glossary", "glossary"), ("Workflows", "/pascal-academy/workflows", "workflows"),
             ("Prompt library", "/pascal-academy/prompt-library", "prompts"),
             ("Agent library", "/pascal-academy/agent-library", "agents")]
    links = "".join(f'<a href="{h}"{CUR if k == active else ""}>{esc(l)}</a>' for l, h, k in items)
    return f"""<div class="ac-bar" role="navigation" aria-label="Pascal Academy">
  <div class="ac-bar-in">
    <a class="ac-bar-home" href="{HUB}">{{{{icon:book-open}}}}<span>Pascal Academy</span></a>
    <div class="ac-bar-links">{links}</div>
    <a class="btn btn-dark btn-sm ac-bar-cta" href="{SIGNUP}">Join a workshop</a>
  </div>
</div>
"""


def workshop():
    return f"""<section class="row ac-workshop" aria-labelledby="ws-title">
    <div>
      <h2 class="h3" id="ws-title">Join Pascal Academy</h2>
      <p>Learn directly from the Pascal team through live workshops.</p>
    </div>
    <a class="btn btn-dark" href="{SIGNUP}">Sign up {{{{icon:arrow-right}}}}</a>
  </section>
"""


DEMO = '<!--#include demo-band title="Ask your first question with your firm\'s context." sub="A walkthrough with your own documents connected."-->\n'


def faq_block(faqs, title_id="faq-title", wrap=True):
    items = "".join(f'<details class="faq-item"><summary>{q}<span class="pm" aria-hidden="true"></span></summary>'
                    f'<div class="ans">{a}</div></details>\n' for q, a in faqs)
    if not wrap:
        return items
    return f"""<section class="row row-pad bg-cream" id="faq" aria-labelledby="{title_id}">
    <div class="faq-wrap">
      <div><h2 class="h2" id="{title_id}">Frequently asked questions</h2></div>
      <div class="faq">
{items}      </div>
    </div>
  </section>
"""


def shot(img, lazy=True, cls=""):
    f, w, h, alt = img
    return (f'<div class="shot{(" " + cls) if cls else ""}"><img src="/assets/shots/{f}" alt="{esc(alt)}" width="{w}" height="{h}"'
            f'{LAZY if lazy else ""} decoding="async"></div>')


# ---------------------------------------------------------------- docs
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


def side_nav(cur):
    def a(href, label, slug):
        return f'<li><a href="{href}"{CUR if slug == cur else ""}>{esc(label)}</a></li>'
    desk = "".join(a(f"/guides/{s}", "AI for " + l.lower() if l != "Hedge funds" else "AI for hedge funds", s) for s, l, *_ in DESK)
    fund = "".join(a(f"/pascal-academy/guides/{s}", l, s) for s, l, _ in FUND)
    lib = "".join(a(p, l, p) for p, l, _ in LIB)
    return f"""<nav class="ac-side" aria-label="Academy guides">
      <p class="ac-side-h">Desk guides</p><ul>{desk}</ul>
      <p class="ac-side-h"><a href="/pascal-academy/ai-fundamentals">AI fundamentals</a></p><ul>{fund}</ul>
      <p class="ac-side-h">Library</p><ul>{lib}</ul>
    </nav>"""


def doc_page(slug):
    d = load(slug)
    desk = d["kind"] == "desk"
    if desk:
        idx = [s for s, *_ in DESK].index(slug)
        _, label, hubdesc, img, panel = DESK[idx]
        seq = [(f"/guides/{s}", "AI for " + l.lower()) for s, l, *_ in DESK]
        crumbs = [["Pascal Academy", HUB], ["Desk guides", HUB + "#guides"], [d["title"], d["path"]]]
        kicker = f"Desk guide · {idx + 1} of {len(DESK)}"
    else:
        idx = [s for s, *_ in FUND].index(slug)
        seq = [(f"/pascal-academy/guides/{s}", l) for s, l, _ in FUND]
        crumbs = [["Pascal Academy", HUB], ["AI fundamentals", "/pascal-academy/ai-fundamentals"], [d["title"], d["path"]]]
        kicker = f"AI fundamentals · Part {idx + 1} of {len(FUND)}"
    # meta row
    parts = [p.strip() for p in d["meta"].split("·") if p.strip() and p.strip() != "Pascal Academy"]
    updated = next((p for p in parts if p.startswith("Updated")), "")
    parts = [p for p in parts if not p.startswith("Updated")]
    upd = [b["h"] for b in d["about"] if b["t"] == "updated"]
    if not updated and upd:
        updated = "Updated " + upd[0]
    parts = [p.replace("~", "") for p in parts]
    meta_html = "".join(f"<span>{esc(p)}</span>" for p in parts)
    # chapters
    chapters = d["chapters"]
    toc = [(c["id"], c["h"]) for c in chapters]
    body = []
    if d["intro"]:
        body.append(f'<div class="ac-intro">{render_blocks(d["intro"])}</div>')
    for c in chapters:
        bl = render_blocks(c["blocks"])
        if re.match(r"further reading", c["h"], re.I):
            bl = link_guides(bl, slug)
        body.append(f'<section class="ac-sec" id="{esc(c["id"])}" aria-labelledby="{esc(c["id"])}-h">'
                    f'<h2 id="{esc(c["id"])}-h">{c["h"]}</h2>\n{bl}\n</section>')
    if d["faqs"]:
        toc.append(("faq", "Frequently asked questions"))
        body.append(f'<section class="ac-sec ac-faq" id="faq" aria-labelledby="faq-h"><h2 id="faq-h">Frequently asked questions</h2>'
                    f'<div class="faq">{faq_block(d["faqs"], wrap=False)}</div></section>')
    about = [b for b in d["about"] if b["t"] == "p"]
    outro = d["outro"]
    if about or outro:
        txt = render_blocks(about + outro)
        lab = "About this guide"
        body.append(f'<aside class="ac-about"><span class="ac-about-mark">{{{{icon:book-open}}}}</span><div><p class="ac-about-h">{lab}</p>{txt}'
                    f'<p class="ac-about-links"><a href="{HUB}">Explore Pascal Academy {{{{icon:arrow-right}}}}</a>'
                    f'<a href="{SIGNUP}">Join a workshop {{{{icon:arrow-right}}}}</a></p></div></aside>')
    # prev / next
    prev = seq[idx - 1] if idx > 0 else None
    nxt = seq[idx + 1] if idx + 1 < len(seq) else None
    pn = '<nav class="ac-pn" aria-label="More guides">'
    pn += (f'<a class="ac-pn-prev" href="{prev[0]}"><span>Previous</span><b>{esc(prev[1][:1].upper() + prev[1][1:])}</b></a>' if prev else "<span></span>")
    pn += (f'<a class="ac-pn-next" href="{nxt[0]}"><span>Next</span><b>{esc(nxt[1][:1].upper() + nxt[1][1:])}</b></a>' if nxt else
           f'<a class="ac-pn-next" href="{HUB}"><span>Back to</span><b>Pascal Academy</b></a>')
    pn += "</nav>"
    toc_html = "".join(f'<li><a href="#{esc(i)}">{re.sub(r"<[^>]+>", "", h)}</a></li>' for i, h in toc)
    title, desc = SEO[slug]
    lead = d["dek"]
    media = ""
    if desk:
        media = f'<div class="ac-dhead-media"><div class="panel {panel}">{shot(img, lazy=False)}</div></div>'
    words = sum(len(re.sub(r"<[^>]+>", " ", x).split()) for x in body)
    meta = {"path": d["path"], "title": title, "description": desc, "crumbs": crumbs, "schema": "article",
            "name": d["title"], "og_kicker": "Pascal Academy", "og_title": d["title"] + (": " + d["dek"] if desk and len(d["dek"]) < 70 else ""),
            "llms": desc, "css": ["academy.css"], "word_limit": max(2000, words + 800),
            "faq_min": min(4, len(d["faqs"])), "lead_min": 8, "lead_max": 60, "priority": 0.7}
    out = front(meta) + bar("desk" if desk else "fund") + f"""<div class="ac ac-docpage">
<div class="frame">
  <header class="ac-dhead{" has-media" if desk else ""}">
    <div class="ac-dhead-copy">
      {{{{crumbs}}}}
      <p class="ac-kick">{kicker}</p>
      <h1 class="ac-h1">{d["title"]}</h1>
      <p class="lead">{lead}</p>
      <div class="ac-meta"><span class="ac-by"><span class="ac-by-mark">{{{{icon:book-open}}}}</span>Pascal Academy</span>{meta_html}{f"<span>{esc(updated)}</span>" if updated else ""}
        <button class="ac-dl" type="button" data-print>{{{{icon:upload}}}}Download PDF</button></div>
    </div>
    {media}
  </header>
  <div class="row ac-docgrid">
    {side_nav(slug)}
    <article class="ac-prose" id="article">
      <details class="ac-toc-m"><summary>On this page {{{{icon:chevron-down}}}}</summary><ol>{toc_html}</ol></details>
{chr(10).join(body)}
      {pn}
    </article>
    <aside class="ac-toc" aria-label="On this page">
      <p class="ac-toc-h">On this page</p>
      <ol data-spy>{toc_html}</ol>
      <a class="ac-toc-top" href="#main">Back to top</a>
    </aside>
  </div>
  {workshop()}
</div>
</div>
<script src="/assets/pages/academy.js" defer></script>
""" + DEMO
    return out


# ---------------------------------------------------------------- hub
def desk_card(i, lazy=True, h="h3"):
    slug, label, desc, img, panel = DESK[i]
    d = load(slug)
    return f"""<a class="ac-gcard" href="/guides/{slug}" data-item>
        <div class="panel {panel} ac-gcard-media">{shot(img, lazy=lazy)}</div>
        <div class="ac-gcard-copy"><p class="ac-gcard-meta">Desk guide · {mins(d["meta"])} min read</p>
        <{h} class="ac-gcard-h">{d["title"]}</{h}><p>{desc}</p></div>
      </a>"""


def fund_row(i, h="h3"):
    slug, label, desc = FUND[i]
    d = load(slug)
    return f"""<a class="ac-drow" href="/pascal-academy/guides/{slug}" data-item>
        <span class="ac-drow-n">{i + 1:02d}</span>
        <span class="ac-drow-copy"><{h} class="ac-drow-h">{esc(label)}</{h}><span class="ac-drow-d">{esc(desc)}</span></span>
        <span class="ac-drow-m">{mins(d["meta"])} min</span>
        <span class="ac-drow-a">{{{{icon:arrow-right}}}}</span>
      </a>"""


def hub_page():
    g = load("lib-glossary")
    w = load("lib-workflows")
    p = load("lib-prompts")
    nterms = sum(len(x["terms"]) for x in g["groups"])
    nwf = sum(len(c["items"]) for c in w["cats"])
    counts = {"/pascal-academy/ai-glossary": f"{nterms} terms · {len(g['groups'])} themes",
              "/pascal-academy/workflows": f"{nwf} workflows",
              "/pascal-academy/prompt-library": f"{len(p['items'])} prompts",
              "/pascal-academy/agent-library": "3 agents · 6 templates"}
    CTA = {"/pascal-academy/ai-glossary": f"Browse {nterms} terms", "/pascal-academy/workflows": f"Browse {nwf} workflows",
           "/pascal-academy/prompt-library": f"Browse {len(p['items'])} prompts", "/pascal-academy/agent-library": "See the agents"}
    lib_cards = "".join(f"""<a class="ac-lcard" href="{href}" data-item>
        <p class="ac-lcard-meta">{counts[href]}</p><h3 class="ac-lcard-h">{esc(label)}</h3><p>{esc(desc)}</p>
        <span class="link">{CTA[href]} {{{{icon:arrow-right}}}}</span></a>""" for href, label, desc in LIB)
    meta = {"path": HUB, "title": "Pascal Academy: Learn AI for Institutional Finance",
            "description": "Practical AI education for investment teams: desk guides, AI fundamentals, a finance AI glossary, workflows, prompts and agents, plus live workshops.",
            "crumbs": [["Pascal Academy", HUB]], "og_kicker": "Pascal Academy", "og_title": "Learn AI for institutional finance",
            "llms": "Pascal Academy home: desk guides for hedge funds, asset managers, investment banks and private equity, a ten-part AI fundamentals series, an AI glossary for finance, workflows, prompts and agents.",
            "css": ["academy.css"], "word_limit": 1100, "faq_min": 0, "priority": 0.8}
    return front(meta) + bar("hub") + f"""<div class="ac ac-hub">
<div class="frame">
  <header class="ac-hhead">
    <div>
      {{{{crumbs}}}}
      <h1 class="ac-hh1">Learn AI for institutional finance</h1>
    </div>
    <div class="ac-hhead-r">
      <p class="lead">Pascal Academy is practical AI education for modern investment teams: guides for every desk, the core concepts explained simply, and tested workflows, prompts and agents.</p>
      <p class="ac-hhead-links"><a class="btn btn-dark" href="#guides">Start learning</a><a class="link" href="{SIGNUP}">Join a live workshop {{{{icon:arrow-right}}}}</a></p>
    </div>
  </header>

  <div class="row ac-browse">
    <div class="ac-browse-bar">
      <h2 class="ac-browse-h">Browse all resources.</h2>
      <label class="ac-search"><span class="sr-only">Search Pascal Academy</span>{{{{icon:search}}}}<input type="search" placeholder="Search guides, concepts and tools" data-filter="#hub-results" autocomplete="off"></label>
    </div>
    <div class="ac-browse-grid" id="hub-results">
      <nav class="ac-cats" aria-label="Academy sections">
        <ol data-spy>
          <li><a href="#guides">Desk guides</a></li>
          <li><a href="#fundamentals">AI fundamentals</a></li>
          <li><a href="#library">Library</a></li>
        </ol>
      </nav>
      <div class="ac-browse-main">
        <section class="ac-grp" id="guides" aria-labelledby="guides-h" data-group>
          <div class="ac-grp-head"><div><h2 class="ac-grp-h" id="guides-h">Guides for every investment desk</h2>
            <p>Practical playbooks for hedge funds, asset managers, bankers, and private markets teams.</p></div></div>
          <div class="ac-gcards">
            {desk_card(0)}
            {desk_card(1)}
            {desk_card(2)}
            {desk_card(3)}
          </div>
        </section>
        <section class="ac-grp" id="fundamentals" aria-labelledby="fund-h" data-group>
          <div class="ac-grp-head"><div><h2 class="ac-grp-h" id="fund-h">AI fundamentals</h2>
            <p>The core concepts behind AI, explained simply.</p></div>
            <a class="btn btn-dark btn-sm" href="/pascal-academy/ai-fundamentals">Go to the series</a></div>
          <div class="ac-drows">
            {"".join(fund_row(i) for i in range(len(FUND)))}
          </div>
        </section>
        <section class="ac-grp" id="library" aria-labelledby="lib-h" data-group>
          <div class="ac-grp-head"><div><h2 class="ac-grp-h" id="lib-h">A growing library of AI resources</h2>
            <p>Concepts, workflows, and reference material for institutional teams.</p></div></div>
          <div class="ac-lcards">{lib_cards}</div>
        </section>
        <p class="ac-empty" hidden>Nothing matches that search. Try a broader term.</p>
      </div>
    </div>
  </div>
  {workshop()}
</div>
</div>
<script src="/assets/pages/academy.js" defer></script>
""" + DEMO


# ---------------------------------------------------------------- AI fundamentals index
def fund_index():
    meta = {"path": "/pascal-academy/ai-fundamentals", "title": "AI Fundamentals for Finance | Pascal Academy",
            "description": "Build a practical understanding of modern AI concepts and how they apply to institutional finance, from LLMs and RAG to agents, embeddings and MCP.",
            "crumbs": [["Pascal Academy", HUB], ["AI fundamentals", "/pascal-academy/ai-fundamentals"]],
            "og_kicker": "Pascal Academy", "og_title": "AI fundamentals for institutional finance",
            "llms": "Index of the ten-part AI Fundamentals series: LLMs, prompt engineering, RAG, AI agents, context windows, knowledge graphs, hallucinations, reasoning models, embeddings and MCP.",
            "css": ["academy.css"], "word_limit": 900, "faq_min": 0, "priority": 0.7}
    more = [("/pascal-academy/workflows", "Workflows", "How AI is applied across research, due diligence, modelling and investment workflows."),
            ("/pascal-academy/prompt-library", "Prompt library", "Browse tested prompts for institutional finance."),
            ("/pascal-academy/ai-glossary", "AI glossary", "Explore AI terminology through an A–Z reference.".replace("–", "-"))]
    more_html = "".join(f"""<a class="ac-lcard" href="{h}"><h3 class="ac-lcard-h">{l}</h3><p>{esc(d)}</p>
        <span class="link">Open {l[:1].lower() + l[1:] if l != "AI glossary" else l} {{{{icon:arrow-right}}}}</span></a>""" for h, l, d in more)
    total = sum(mins(load(s)["meta"]) or 0 for s, *_ in FUND)
    return front(meta) + bar("fund") + f"""<div class="ac ac-index">
<div class="frame">
  <header class="ac-phead">
    {{{{crumbs}}}}
    <h1 class="ac-ph1">AI fundamentals</h1>
    <p class="lead">Build a practical understanding of modern AI concepts and learn how they apply to institutional finance.</p>
    <p class="ac-phead-meta"><span>{len(FUND)} guides</span><span>{total} min in total</span><span>Beginner-friendly with advanced sections</span></p>
  </header>
  <section class="row ac-pbody" aria-labelledby="vocab-h">
    <div class="ac-pbody-head"><h2 class="ac-grp-h" id="vocab-h">Build the vocabulary</h2>
      <p>Short explainers for the ideas that keep showing up in institutional AI work.</p></div>
    <div class="ac-drows ac-drows-lg">
      {"".join(fund_row(i) for i in range(len(FUND)))}
    </div>
  </section>
  <section class="row ac-pbody" aria-labelledby="more-h">
    <div class="ac-pbody-head"><h2 class="ac-grp-h" id="more-h">More from Pascal Academy</h2></div>
    <div class="ac-lcards ac-lcards-3">{more_html}</div>
  </section>
  {workshop()}
</div>
</div>
<script src="/assets/pages/academy.js" defer></script>
""" + DEMO


# ---------------------------------------------------------------- library shell
def lib_head(h1, lead, crumb, side=""):
    return f"""<header class="ac-phead{" has-side" if side else ""}">
    <div>
      {{{{crumbs}}}}
      <h1 class="ac-ph1">{h1}</h1>
      <p class="lead">{lead}</p>
    </div>
    {side}
  </header>"""


def search_box(target, placeholder):
    return (f'<label class="ac-search"><span class="sr-only">{esc(placeholder)}</span>{{{{icon:search}}}}'
            f'<input type="search" placeholder="{esc(placeholder)}" data-filter="{target}" autocomplete="off"></label>')


def glossary_page():
    g = load("lib-glossary")
    n = sum(len(x["terms"]) for x in g["groups"])
    cats = "".join(f'<li><a href="#{slugify(x["name"])}">{esc(x["name"])}<span>{len(x["terms"])}</span></a></li>' for x in g["groups"])
    groups = []
    for x in g["groups"]:
        terms = "".join(f"""<div class="ac-term" id="{slugify(t["term"])}" data-item>
            <div class="ac-term-k"><h4>{t["term"]}</h4><span class="ac-tag">{esc(t["tag"].upper() if len(t["tag"]) <= 4 else t["tag"].title())}</span></div>
            <p>{t["def"]}</p></div>""" for t in x["terms"])
        groups.append(f"""<section class="ac-grp" id="{slugify(x["name"])}" aria-labelledby="{slugify(x["name"])}-h" data-group>
          <div class="ac-grp-head"><div><h3 class="ac-grp-h" id="{slugify(x["name"])}-h">{x["name"]}</h3><p>{x["desc"]}</p></div><span class="ac-grp-n">{len(x["terms"])} terms</span></div>
          <div class="ac-terms">{terms}</div>
        </section>""")
    meta = {"path": "/pascal-academy/ai-glossary", "title": "AI Glossary for Finance | Pascal Academy",
            "description": "A finance-focused reference of AI terms for investment teams, covering LLMs, RAG, agents, embeddings, MCP and governance, grouped by theme with search.",
            "crumbs": [["Pascal Academy", HUB], ["AI glossary", "/pascal-academy/ai-glossary"]],
            "og_kicker": "Pascal Academy", "og_title": "AI glossary for finance",
            "llms": f"A finance-focused glossary of {n} AI terms for investment teams, grouped into themes: models and foundations, core AI and agents, retrieval and knowledge, prompting, integration and platform, finance and governance.",
            "css": ["academy.css"], "word_limit": 4200, "lead_min": 8, "priority": 0.7}
    return front(meta) + bar("glossary") + f"""<div class="ac ac-lib">
<div class="frame">
  {lib_head("AI glossary for finance", "An A-to-Z reference of AI terms written for investment teams.", "AI glossary")}
  <div class="row ac-libgrid" id="gl-results">
    <aside class="ac-cats">
      {search_box("#gl-results", f"Search {n} terms")}
      <nav aria-label="Glossary themes"><p class="ac-cats-h">Themes</p><ol data-spy>{cats}</ol></nav>
    </aside>
    <div class="ac-libmain">
      <div class="ac-libintro"><h2 class="ac-grp-h">Browse the glossary.</h2>
        <p>Finance-focused definitions grouped by theme. Search or filter to find the terms that come up in research, modelling, and AI discussions. For the longer explanations, read the <a href="/pascal-academy/ai-fundamentals">AI fundamentals</a> series.</p></div>
      {"".join(groups)}
      <p class="ac-empty" hidden>No term matches that search.</p>
    </div>
  </div>
  {faq_block(g["faqs"])}
  {workshop()}
</div>
</div>
<script src="/assets/pages/academy.js" defer></script>
""" + DEMO


def workflows_page():
    w = load("lib-workflows")
    n = sum(len(c["items"]) for c in w["cats"])
    stages = "".join(f"""<div class="ac-stage"><span class="ac-stage-n">{s["n"]}</span><h3>{s["name"]}</h3>
        <p class="ac-stage-q">{s["q"]}</p><p>{s["d"]}</p></div>""" for s in w["stages"])
    cats = "".join(f'<li><a href="#{slugify(c["name"])}">{esc(c["name"])}<span>{len(c["items"])}</span></a></li>' for c in w["cats"])
    groups = []
    for c in w["cats"]:
        items = []
        for it in c["items"]:
            steps = "".join(f"<li>{s}</li>" for s in it["steps"])
            flow = "".join(f"<li>{esc(f)}</li>" for f in it["flow"])
            inputs = "".join(f"<li>{i.strip()}</li>" for i in it["inputs"].split("·") if i.strip())
            items.append(f"""<details class="ac-wf" id="{esc(it["id"])}" data-item>
            <summary><span class="ac-wf-t"><h4>{it["title"]}</h4><span>{it["desc"]}</span></span><span class="ac-wf-chev">{{{{icon:plus}}}}</span></summary>
            <div class="ac-wf-body">
              <ol class="ac-flow" aria-label="Stages">{flow}</ol>
              <div class="ac-wf-cols">
                <div><p class="ac-wf-k">How it works</p><ol class="ac-steps">{steps}</ol></div>
                <div><p class="ac-wf-k">Inputs</p><ul class="ac-inputs">{inputs}</ul>
                  <p class="ac-wf-k">Output</p><p>{it["output"]}</p>
                  <p><a class="link" href="{{{{demo_url}}}}">Try this workflow {{{{icon:arrow-right}}}}</a></p></div>
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
            "css": ["academy.css"], "word_limit": 3200, "faq_min": 0, "priority": 0.7}
    return front(meta) + bar("workflows") + f"""<div class="ac ac-lib">
<div class="frame">
  {lib_head("Workflows", "How AI turns financial work into repeatable processes. See how real financial tasks can be broken down, automated, and run with AI.", "Workflows")}
  <section class="row ac-anat" aria-labelledby="anat-h">
    <div class="ac-pbody-head"><h2 class="ac-grp-h" id="anat-h">The anatomy of a workflow</h2>
      <p>Every workflow breaks a financial task into five stages: define the job, gather context, run the process, produce the deliverable, and review the result.</p></div>
    <div class="ac-stages">{stages}</div>
  </section>
  <div class="row ac-libgrid" id="wf-results">
    <aside class="ac-cats">
      {search_box("#wf-results", f"Search {n} workflows")}
      <nav aria-label="Workflow categories"><p class="ac-cats-h">Categories</p><ol data-spy>{cats}</ol></nav>
    </aside>
    <div class="ac-libmain">
      <div class="ac-libintro"><h2 class="ac-grp-h">Browse the library.</h2>
        <p>Step-by-step workflows for the tasks analysts do every day. Each one shows the inputs, process, and deliverable. Open a workflow to see how it runs, or use ready-made <a href="/pascal-academy/prompt-library">prompts</a> and <a href="/pascal-academy/agent-library">agents</a> for the same tasks.</p></div>
      {"".join(groups)}
      <p class="ac-empty" hidden>No workflow matches that search.</p>
    </div>
  </div>
  {workshop()}
</div>
</div>
<script src="/assets/pages/academy.js" defer></script>
""" + DEMO


def prompts_page():
    p = load("lib-prompts")
    cats = []
    for it in p["items"]:
        if it["cat"] not in cats:
            cats.append(it["cat"])
    nav = "".join(f'<li><a href="#{slugify(c)}">{esc(c)}<span>{sum(1 for i in p["items"] if i["cat"] == c)}</span></a></li>' for c in cats)
    groups = []
    for c in cats:
        cards = "".join(f"""<article class="ac-prompt" id="{slugify(it["title"])}" data-item>
            <div class="ac-prompt-head"><span class="ac-prompt-n">{it["n"]}</span><h4>{it["title"]}</h4></div>
            <p class="ac-prompt-when">{it["when"]}</p>
            <div class="ac-prompt-box"><pre>{it["prompt"]}</pre>
              <button type="button" class="ac-copy" data-copy>{{{{icon:file-text}}}}<span>Copy prompt</span></button></div>
          </article>""" for it in p["items"] if it["cat"] == c)
        groups.append(f"""<section class="ac-grp" id="{slugify(c)}" aria-labelledby="{slugify(c)}-h" data-group>
          <div class="ac-grp-head"><div><h3 class="ac-grp-h" id="{slugify(c)}-h">{esc(c)}</h3></div></div>
          <div class="ac-prompts">{cards}</div>
        </section>""")
    comps = "".join(f"<tr><td>{x['k']}</td><td>{x['v']}</td></tr>" for x in p["components"])
    mistakes = [m for m in p["mistakes"] if not m["k"].lower().startswith("chain")]
    cot = next((m for m in p["mistakes"] if m["k"].lower().startswith("chain")), None)
    mis = "".join(f'<div class="ac-cell"><h4>{m["k"]}</h4><p>{m["v"]}</p></div>' for m in mistakes)
    bounds = "".join(f'<div class="ac-cell"><h3>{m["k"]}</h3><p>{m["v"]}</p></div>' for m in p["bounds"])
    cot_html = (f'<aside class="ac-co ac-co-tip"><p class="ac-co-lab"><span class="ac-co-ic">{{{{icon:zap}}}}</span>{cot["k"]}</p>'
                f'<div class="ac-co-body"><p>{cot["v"]}</p></div></aside>') if cot else ""
    meta = {"path": "/pascal-academy/prompt-library", "title": "AI Prompts for Finance | Pascal Academy",
            "description": f"{len(p['items'])} tested AI prompts for institutional finance: company research, earnings, modelling, comps, IC memos, portfolio and investor communication.",
            "crumbs": [["Pascal Academy", HUB], ["Prompt library", "/pascal-academy/prompt-library"]],
            "og_kicker": "Pascal Academy", "og_title": "Tested AI prompts for finance",
            "llms": f"{len(p['items'])} copy-ready AI prompts for investment teams, plus how to structure a finance prompt and when AI should not make the call.",
            "css": ["academy.css"], "word_limit": 3400, "lead_min": 10, "priority": 0.7}
    return front(meta) + bar("prompts") + f"""<div class="ac ac-lib">
<div class="frame">
  {lib_head("AI prompts for finance", "Tested prompts for research, memos and modelling. Copy, adapt and run.", "Prompt library")}
  <section class="row ac-howto" aria-labelledby="howto-h">
    <h2 class="ac-grp-h" id="howto-h">Start with the task.</h2>
    <p>Each card contains a structured prompt you can copy and adapt to your workflow. Replace the bracketed fields with your company, data and specific requirements. Add the context the model needs, then specify the format you want in the output.</p>
  </section>
  <div class="row ac-libgrid" id="pr-results">
    <aside class="ac-cats">
      {search_box("#pr-results", f"Search {len(p['items'])} prompts")}
      <nav aria-label="Prompt categories"><p class="ac-cats-h">Categories</p><ol data-spy>{nav}</ol></nav>
    </aside>
    <div class="ac-libmain">
      <div class="ac-libintro"><h2 class="ac-grp-h">Browse tested prompts.</h2>
        <p>Filter by category or search by task. Each card includes a structured prompt you can copy and adapt for your workflow. The <a href="/pascal-academy/guides/prompt-engineering">prompt engineering guide</a> explains why these patterns work.</p></div>
      {"".join(groups)}
      <p class="ac-empty" hidden>No prompt matches that search.</p>
    </div>
  </div>
  <section class="row ac-pbody ac-better" aria-labelledby="better-h">
    <div class="ac-pbody-head"><h2 class="ac-grp-h" id="better-h">What makes a finance prompt effective.</h2>
      <p>Output quality reflects input quality. A prompt that produces a useful result for an investment task has a recognizable structure.</p></div>
    <div class="ac-better-grid">
      <div class="ac-table ac-table-k"><table><thead><tr><th>Part</th><th>Example</th></tr></thead><tbody>{comps}</tbody></table></div>
      <div>
        <h3 class="ac-sub-h">Common mistakes to avoid</h3>
        <div class="ac-cells ac-cells-2">{mis}</div>
        {cot_html}
      </div>
    </div>
  </section>
  <section class="row ac-pbody" aria-labelledby="bounds-h">
    <div class="ac-pbody-head"><h2 class="ac-grp-h" id="bounds-h">When AI should not make the call.</h2>
      <p>AI accelerates the analytical process, but investment judgment stays with the analyst. There are specific scenarios where AI should not be relied on for final outputs or decisions.</p></div>
    <div class="ac-cells ac-cells-4">{bounds}</div>
  </section>
  {faq_block(p["faqs"])}
  {workshop()}
</div>
</div>
<script src="/assets/pages/academy.js" defer></script>
""" + DEMO


def agents_page():
    src = (ROOT.parent.parent / "_academy_src/txt/pascal-academy_agent-library.txt").read_text()
    faqs = []
    lines = src.splitlines()
    qs = ["What are AI agents for finance?", "What is Pascal AI?", "How do AI agents extract data from financial filings?",
          "Can AI agents generate investment research reports?", "Are Pascal's AI agents secure for institutional use?"]
    # answers are in page order after the FAQ heading; questions come from the live accordion
    ans = [l[4:] for l in lines[lines.index("[h2] Frequently asked questions."):] if l.startswith("[p] ")]
    faq_q = load_agent_faq_questions()
    faqs = list(zip(faq_q or qs, ans))
    agents = [
        ("Analysis", "01", "Generative Matrix",
         "Filter companies, then analyze them using AI to answer your specific questions and get detailed insights across your filtered company set.",
         ["Select companies", "Define question", "Analyze", "Compare"], "Works with", ["Public companies", "Smart Search", "My Vault"],
         ("shot-agent-table.webp", 1600, 844, "Generative Matrix style output: a comparison table across companies with citations"), "panel-dark"),
        ("Extraction", "02", "KPI Extractor",
         "Automatically extract tables and graphs from company filings and your own documents into Excel. No more manual copy-paste.",
         ["Select company", "Select source", "Select period", "Extract"], "Sources", ["Annual Report", "Earnings Presentation", "Quarterly Report", "My Vault"],
         ("shot-excel.webp", 1600, 504, "Excel model with the Pascal KPI Extractor panel planning its steps"), "panel-cream"),
        ("Generation", "03", "Research Memo Generator",
         "Generate customized company research reports using your fund's template. No more hours of research, just a click.",
         ["Select sources", "Choose template", "Generate", "Review"], "Templates", ["Company Primer", "Earnings Analysis", "IPO Prospectus", "Credit Memo", "+ Custom"],
         ("shot-word.webp", 1316, 660, "Word research memo generated by Pascal from a template"), "panel-dark"),
    ]
    rows = []
    for i, (cat, n, name, desc, steps, klab, kv, img, panel) in enumerate(agents):
        st = "".join(f"<li>{esc(s)}</li>" for s in steps)
        kvs = "".join(f"<li>{esc(x)}</li>" for x in kv)
        rows.append(f"""<section class="row ac-agent{" flip" if i % 2 else ""}" id="{slugify(name)}" aria-labelledby="{slugify(name)}-h">
    <div class="ac-agent-copy">
      <p class="ac-kick">{cat} · {n}</p>
      <h3 class="ac-agent-h" id="{slugify(name)}-h">{name}</h3>
      <p>{esc(desc)}</p>
      <ol class="ac-flow">{st}</ol>
      <p class="ac-wf-k">{klab}</p><ul class="ac-inputs">{kvs}</ul>
      <p><a class="link" href="{{{{demo_url}}}}">Run agent {{{{icon:arrow-right}}}}</a></p>
    </div>
    <div class="ac-agent-media"><div class="panel {panel}">{shot(img)}</div></div>
  </section>""")
    why = [("01", "Built for investment work", "Each agent is designed around a defined investment workflow, from screening and extraction to memo generation and portfolio monitoring."),
           ("02", "Simple setup", "Select the companies, sources, and output format you need. The agent applies the workflow and produces a structured result."),
           ("03", "Source-backed outputs", "Every output includes citations to the underlying sources, making facts, figures, and conclusions easy to trace and verify.")]
    how = [("Step 01", "Select your inputs", "Choose companies, filings, documents, or your own uploaded research. The agent works with public filings and your internal files side by side."),
           ("Step 02", "Define what you need", "Pick a template, specify a question, or select which KPIs to extract. The agent's guided setup walks you through the options."),
           ("Step 03", "Get a cited output", "The agent processes the inputs and returns a structured result. Every number, claim, and data point traces back to the source line it came from.")]
    tpl = [("01", "Company Primer", "A structured one-page overview of any public company. Business model, revenue segments, competitive position, key financials.", "/pascal-academy/workflows#company-primer"),
           ("02", "Earnings Analysis", "From earnings release to structured analysis. KPIs, guidance changes, management commentary, and estimate revisions.", "/pascal-academy/workflows#earnings-summary"),
           ("03", "IPO Prospectus", "Summarize and structure an IPO prospectus. Business overview, use of proceeds, risk factors, and financial highlights.", "/pascal-academy/workflows#ipo-prospectus"),
           ("04", "Annual Report Summariser", "Turn a full annual report into a structured summary. MD&A, financial statements, segment performance, and forward-looking commentary.", "/pascal-academy/workflows#annual-report"),
           ("05", "Credit Memo", "Generate a credit memo from financial data and filings. Credit metrics, covenant analysis, repayment capacity, and risk assessment.", "{{demo_url}}"),
           ("+", "Create Custom Template", "Start from scratch. Define your own sections, data points, and structure in the template builder.", "{{demo_url}}")]
    own = [("1", "Task", "What needs to get done?"), ("2", "Inputs", "What companies, filings, or documents does it need?"),
           ("3", "Process", "What should it do with those inputs?"), ("4", "Output", "What should the finished result look like?"),
           ("5", "Review", "How will you verify the result is accurate?")]
    cells = lambda xs, hl="h3": "".join(f'<div class="ac-cell"><span class="ac-cell-n">{a}</span><{hl}>{b}</{hl}><p>{esc(c)}</p></div>' for a, b, c in xs)
    tpls = "".join(f'<a class="ac-cell ac-cell-link" href="{h}"><span class="ac-cell-n">{a}</span><h3>{b}</h3><p>{esc(c)}</p>'
                   f'<span class="ac-cell-arr">{{{{icon:arrow-right}}}}</span></a>' for a, b, c, h in tpl)
    meta = {"path": "/pascal-academy/agent-library", "title": "AI Agents for Finance | Pascal Academy",
            "description": "Pascal's AI agents for institutional finance: screen company universes, extract KPIs from filings into Excel, and generate research memos from templates.",
            "crumbs": [["Pascal Academy", HUB], ["Agent library", "/pascal-academy/agent-library"]],
            "og_kicker": "Pascal Academy", "og_title": "AI agents for investment research",
            "llms": "Pascal's agent library: Generative Matrix (screen and analyse companies), KPI Extractor (filings to Excel), Research Memo Generator (template reports), with research templates and a framework for building your own agent.",
            "css": ["academy.css"], "word_limit": 1500, "lead_min": 8, "priority": 0.7}
    return front(meta) + bar("agents") + f"""<div class="ac ac-lib ac-agents">
<div class="frame">
  {lib_head("AI agents for finance", "Purpose-built agents for institutional finance. Research, extract and generate.", "Agent library")}
  <section class="row ac-pbody" aria-labelledby="why-h">
    <div class="ac-pbody-head"><h2 class="ac-grp-h" id="why-h">Agents built around how investment teams actually work.</h2></div>
    <div class="ac-cells ac-cells-3">{cells(why)}</div>
  </section>
  <section class="row ac-pbody ac-pbody-tight" aria-labelledby="all-h" id="agents">
    <div class="ac-pbody-head"><h2 class="ac-grp-h" id="all-h">Agents for investment research.</h2>
      <p>Run repeatable finance workflows, from research to memo generation. Each agent handles a specific task and delivers a structured output. For the concepts behind them, read <a href="/pascal-academy/guides/ai-agents">AI agents explained</a>.</p></div>
  </section>
  {"".join(rows)}
  <section class="row ac-pbody" aria-labelledby="how-h">
    <div class="ac-pbody-head"><h2 class="ac-grp-h" id="how-h">Build for the task.</h2>
      <p>Every Pascal agent follows the same pattern. You define what you need, the agent gathers and processes the inputs, and you get a structured output with citations back to the source.</p></div>
    <div class="ac-cells ac-cells-3">{cells(how)}</div>
  </section>
  <section class="row ac-pbody" aria-labelledby="tpl-h">
    <div class="ac-pbody-head"><h2 class="ac-grp-h" id="tpl-h">Pre-built templates for common research outputs.</h2>
      <p>The Research Memo Generator comes with templates designed for the outputs investment teams produce regularly. Each defines the structure, sections, and data points the agent should populate. You can also build your own from scratch.</p></div>
    <div class="ac-cells ac-cells-3">{tpls}</div>
  </section>
  <section class="row ac-pbody" aria-labelledby="own-h">
    <div class="ac-pbody-head"><h2 class="ac-grp-h" id="own-h">Create an agent for your workflow.</h2>
      <p>The agents above cover common tasks, but every investment team has workflows specific to how they work. Start with a task you repeat every week and turn it into a reusable agent. The <a href="/pascal-academy/workflows">workflow library</a> shows the same five stages applied to real tasks.</p></div>
    <div class="ac-cells ac-cells-5">{cells(own)}</div>
  </section>
  {faq_block(faqs)}
  {workshop()}
</div>
</div>
<script src="/assets/pages/academy.js" defer></script>
""" + DEMO


def load_agent_faq_questions():
    from bs4 import BeautifulSoup
    s = BeautifulSoup((ROOT.parent.parent / "_academy_src/pascal-academy_agent-library.html").read_text(), "html.parser")
    out = []
    for b in s.find("main").find_all("button", attrs={"aria-expanded": True}):
        q = " ".join(b.get_text(" ").replace("+", " ").split())
        if q.endswith("?"):
            out.append(esc(q).replace("&#x27;", "'"))
    return out


# ---------------------------------------------------------------- main
def main():
    STAGING.mkdir(exist_ok=True)
    pages = {"academy-hub": hub_page(), "academy-fundamentals": fund_index(), "academy-glossary": glossary_page(),
             "academy-workflows": workflows_page(), "academy-prompts": prompts_page(), "academy-agents": agents_page()}
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
