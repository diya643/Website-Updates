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
    "ai-for-hedge-funds": ("AI for Hedge Funds: Complete Guide | Pascal Academy", "A practical guide to AI for hedge funds: use cases, benefits, challenges and implementation, from research automation and portfolio monitoring to production."),
    "ai-for-asset-management": ("AI for Asset Management: Guide | Pascal Academy", "A practical guide to AI for asset managers: RFP automation, research, portfolio monitoring, compliant client reporting, and the architecture to run it safely."),
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
                           f'<div class="ac-co-body">{body}<p><a class="ac-co-link" href="{SIGNUP}">Ask about team training</a></p></div></aside>')
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
        <button class="btn btn-dark" type="submit">Email me the PDF</button>
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



# ---------------------------------------------------------------- v3: Glean Content Hub blueprint
# Light framed hero with a big title + description, a colourful featured band, "Browse all ..." with a pill search,
# a left category list and rows of Glean-style cards (grey card, dotted thumbnail, bezel-framed gradient screen).
# Guides use Glean's article layout: light header with the thumbnail on the right, sticky contents with reading progress.
# No arrows anywhere (user rule, 11 Oct 2026). No icon-chip widgets on cards.
def I(name):
    return "{{icon:" + name + "}}"


SCRIPT = '<script src="/assets/pages/academy3.js" defer></script>\n'
GRADS = ["g-teal", "g-mint", "g-sea", "g-cream", "g-deep"]
DEMO = '<!--#include demo-band title="Ask your first question with your firm\'s context." sub="A walkthrough with your own documents connected."-->\n'

FUND_CHIPS = {
    "large-language-models": [("layers", "Pre-training"), ("edit", "Supervised fine-tuning"), ("users", "Human feedback (RLHF)")],
    "prompt-engineering": [("message", "Zero-shot prompting"), ("list-checks", "Few-shot prompting"), ("git-branch", "Chain-of-thought")],
    "rag-retrieval-augmented-generation": [("upload", "Document ingestion"), ("database", "Vector databases"), ("search", "Hybrid search")],
    "ai-agents": [("brain", "The model"), ("settings", "Tools"), ("database", "Memory")],
    "context-windows": [("scan-text", "Conversation summarisation"), ("file-search", "Retrieve with RAG"), ("refresh", "Sliding window")],
    "knowledge-graphs": [("network", "Nodes"), ("link", "Edges"), ("layers", "Organising principles")],
    "ai-hallucinations": [("alert", "Knowledge gaps"), ("repeat", "Pattern completion"), ("database", "Training data errors")],
    "reasoning-models": [("route", "Reasoning traces"), ("clock", "Extended thinking"), ("calculator", "Mathematics and logic")],
    "embeddings": [("target", "The geometry of meaning"), ("scale", "Similarity metrics"), ("search", "Semantic search")],
    "model-context-protocol": [("plug", "The MCP client"), ("server", "The MCP server"), ("send", "Communication")],
}


def grad(i):
    return GRADS[i % len(GRADS)]


# ---------- thumbnails (Glean: dotted plate, bezel, gradient screen, colour swoosh)
def chips_html(items):
    return "".join(f'<span class="tc tc-{n}">{I(ic)}<b>{esc(lbl)}</b></span>' for n, (ic, lbl) in enumerate(items[:3]))


def screen(g, kind, payload, lazy=True):
    if kind == "shot":
        f, w, h, alt = payload
        inner = f'<img src="/assets/shots/{f}" alt="{esc(alt)}" width="{w}" height="{h}"{LAZY if lazy else ""} decoding="async">'
        return f'<div class="th-scr th-shot {g}">{inner}</div>'
    if kind == "chips":
        return f'<div class="th-scr {g}"><div class="tcs">{chips_html(payload)}</div></div>'
    if kind == "code":
        return f'<div class="th-scr {g}"><div class="tcode"><span class="tcode-bar"><i></i><i></i><i></i></span><pre>{payload}</pre></div></div>'
    if kind == "flow":
        steps = "".join(f"<li>{esc(x)}</li>" for x in payload)
        return f'<div class="th-scr {g}"><ol class="tflow">{steps}</ol></div>'
    if kind == "term":
        term, tag, line = payload
        return (f'<div class="th-scr {g}"><div class="tterm"><span class="tterm-tag">{esc(tag)}</span><b>{term}</b>'
                f'<span class="tterm-l"></span><span class="tterm-l s"></span></div></div>')
    return f'<div class="th-scr {g}"></div>'


def thumb(g, kind, payload, lazy=True, cls=""):
    return f'<div class="th{(" " + cls) if cls else ""}" aria-hidden="{"false" if kind == "shot" else "true"}"><div class="th-bz">{screen(g, kind, payload, lazy)}</div></div>'


def card(href, th, title, tag="", meta="", desc="", h="h3", cls="", attrs=""):
    tag_h = f'<span class="pill">{tag}</span>' if tag else ""
    desc_h = f'<p class="gc-d">{desc}</p>' if desc else ""
    meta_h = f'<p class="gc-m">{meta}</p>' if meta else ""
    c = f" {cls}" if cls else ""
    return f'<a class="gc{c}" href="{href}"{attrs}>{th}<div class="gc-b">{tag_h}<{h} class="gc-t">{title}</{h}>{desc_h}{meta_h}</div></a>'


def desk_thumb(i, lazy=True, cls=""):
    slug, label, desc, img, panel = DESK[i]
    return thumb(grad(i), "shot", img, lazy, cls)


def fund_thumb(i, cls=""):
    slug = FUND[i][0]
    return thumb(grad(i + 1), "chips", FUND_CHIPS[slug], cls=cls)


def desk_card(i, h="h3"):
    slug, label, desc, img, panel = DESK[i]
    d = load(slug)
    return card(f"/guides/{slug}", desk_thumb(i), d["title"], "Desk guide", f'{mins(d["meta"])} min read', esc(desc), h, attrs=" data-item")


def fund_card(i, h="h3"):
    slug, label, desc = FUND[i]
    d = load(slug)
    return card(f"/pascal-academy/guides/{slug}", fund_thumb(i), esc(label), f"Part {i + 1:02d}", f'{mins(d["meta"])} min read', esc(desc), h, attrs=" data-item")


# ---------- page furniture
def hero(title, em, lead, crumbs=True, extra=""):
    return f"""<div class="frame">
  <header class="hh">
    <div class="hh-l">
      {"{{crumbs}}" if crumbs else ""}
      <h1 class="hh-t">{title} <em>{em}</em></h1>
    </div>
    <div class="hh-r"><p class="lead">{lead}</p>{extra}</div>
  </header>
"""


def band(inner, cls=""):
    return f'<section class="fb{(" " + cls) if cls else ""}" aria-label="Featured"><div class="fb-in">{inner}</div></section>\n'


def tiles(items, label="Featured"):
    """Glean's expanding cards: [(tag, title, desc, href, grad, kind, payload)]"""
    out = []
    for n, (tag, title, desc, href, g, kind, payload) in enumerate(items):
        el = "a" if href else "div"
        out.append(f"""<{el} class="tl {g}{" on" if n == 0 else ""}"{f' href="{href}"' if href else ' tabindex="0"'} data-tile>
        <span class="pill pill-l">{tag}</span>
        <span class="tl-art">{screen(g, kind, payload) if kind else ""}</span>
        <span class="tl-copy"><b class="tl-t">{title}</b><span class="tl-d">{desc}</span></span>
      </{el}>""")
    return f'<div class="tls" role="list" aria-label="{label}">{"".join(out)}</div>'


def browse(title, placeholder, target):
    return f"""<div class="bb">
      <h2 class="bb-t">{title}</h2>
      <label class="sp"><span class="sr-only">{esc(placeholder)}</span><input type="search" placeholder="{esc(placeholder)}" data-filter="{target}" autocomplete="off">{I("search")}</label>
    </div>"""


def side(items, label):
    lis = "".join(f'<li><a href="#{slugify(n) if not n.startswith("#") else n[1:]}">{esc(t)}</a></li>' for n, t in items)
    return f'<nav class="sd" aria-label="{label}"><ol data-spy>{lis}</ol></nav>'


def grp(gid, title, inner, go=None, sub="", h="h2", cls=""):
    btn = f'<a class="btn btn-dark" href="{go[1]}">{go[0]}</a>' if go else ""
    return f"""<section class="sx{(" " + cls) if cls else ""}" id="{gid}" aria-labelledby="{gid}-h" data-group>
        <div class="sx-h"><div><{h} class="sx-t" id="{gid}-h">{title}</{h}>{f'<p class="sx-s">{sub}</p>' if sub else ""}</div>{btn}</div>
        {inner}
      </section>"""


def row(cards, cls=""):
    return f'<div class="gr{(" " + cls) if cls else ""}">{"".join(cards)}</div>'


def workshop():
    return f"""<section class="ws" aria-labelledby="ws-t">
    <div class="ws-in">
      <div><h2 class="ws-t" id="ws-t">Join Pascal Academy</h2><p>Learn directly from the Pascal team through live workshops.</p></div>
      <a class="btn btn-dark" href="{SIGNUP}">Sign up</a>
    </div>
  </section>
"""


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


def counts():
    g, w, p = load("lib-glossary"), load("lib-workflows"), load("lib-prompts")
    return {"terms": sum(len(x["terms"]) for x in g["groups"]), "themes": len(g["groups"]),
            "workflows": sum(len(c["items"]) for c in w["cats"]), "prompts": len(p["items"]),
            "fund_min": sum(mins(load(s)["meta"]) or 0 for s, *_ in FUND)}


RELATED = {  # in-copy links from each guide to the matching Pascal page
    "ai-for-hedge-funds": ("/solutions/hedge-funds", "Pascal for hedge funds"),
    "ai-for-asset-management": ("/solutions/asset-wealth-management", "Pascal for asset and wealth managers"),
    "ai-for-investment-banking": ("/solutions/banking", "Pascal for banks and financial institutions"),
    "ai-for-private-equity": ("/solutions/private-equity-credit", "Pascal for private equity and private credit"),
    "knowledge-graphs": ("/platform/context-graph", "the Pascal context graph"),
    "model-context-protocol": ("/platform/mcp-apis", "Pascal MCP and APIs"),
    "ai-agents": ("/pascal-agents", "Pascal Agents"),
    "ai-hallucinations": ("/ask-pascal/cited-research", "cited research in Ask Pascal"),
    "rag-retrieval-augmented-generation": ("/ask-pascal/cited-research", "cited research in Ask Pascal"),
}
# Extra FAQs for the two short desk guides: questions on their own chapters, answers are the guides' own sentences.
EXTRA_FAQS = {
    "ai-for-investment-banking": [
        ("How does AI help build a comparable companies set?", "AI can propose a peer universe with a rationale for every name and assemble the first-pass table, flagging where definitions differ between companies. The judgement, which peers truly belong, which to trim, stays with the banker."),
        ("How should bankers use AI to read a CIM?", "With retrieval, a team can interrogate it directly, customer concentration, margin bridge, the assumptions behind the projections, and get cited answers to work from. A CIM is a sell document; AI helps you read it sceptically, but the scepticism is yours."),
        ("Should AI do the valuation maths?", "Use AI for the narrative and assumptions around a valuation, laying out drivers, sensitivities and the comparable context. The math stays in an auditable spreadsheet where every input can be checked."),
    ],
    "ai-for-private-equity": [
        ("How does AI help with deal sourcing?", "AI helps by reading company descriptions, news, filings and web presence, then scoring each candidate against your stated criteria, sector, size, growth, business model, ownership. The output is a ranked, annotated longlist with a reason attached to every entry."),
        ("How does AI speed up commercial due diligence?", "With retrieval over the data room, a deal team can ask questions of hundreds of documents at once and get answers that point back to the exact page they came from. Treat every answer as a lead to verify."),
        ("Can AI help with portfolio monitoring?", "AI can normalise portfolio company packs into a consistent shape, extract the KPIs that matter, and flag the exceptions worth a partner's attention. Every extracted metric still needs a source and a spot-check before it drives a decision."),
    ],
}
MONTHS = {m: i + 1 for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                           "September", "October", "November", "December"])}


def iso_date(txt):
    m = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(?:(\d{1,2}),\s*)?(\d{4})", txt or "")
    return f"{m.group(3)}-{MONTHS[m.group(1)]:02d}-{int(m.group(2) or 1):02d}" if m else None


HUB_FAQS = [
    ("What is Pascal Academy?", "Practical AI education for modern investment teams: desk guides for hedge funds, asset managers, bankers and private equity, a ten-part AI fundamentals series, and a library of AI terms, workflows, prompts and agents."),
    ("Who is Pascal Academy for?", "Portfolio managers, analysts, heads of research, bankers and private markets teams, and the technology and operations leaders who support them."),
    ("Can I download the guides as PDFs?", "Yes. Every desk guide and AI fundamentals guide has a Download the PDF button; enter your work email and we send the PDF to your inbox."),
    ("Does Pascal Academy run workshops for teams?", "Yes. The Pascal team runs live workshops planned around your firm. Sign up and we will follow up to plan one."),
]

DESK_FAQS = [
    ("Which desks do the Pascal Academy guides cover?", "Hedge funds, asset management, investment banking and private equity, with one guide for each desk."),
    ("How long are the desk guides?", "Between 20 and 24 minutes each, about an hour and a half to read all four."),
    ("Where should I start?", "Start with the guide for your desk. For the concepts underneath, the AI fundamentals series covers large language models, RAG, agents, knowledge graphs and MCP."),
    ("Can I get a desk guide as a PDF?", "Yes. Open the guide and use Download the PDF; enter your work email and we send it to your inbox."),
]
FUND_FAQS = [
    ("What does the AI fundamentals series cover?", "Ten guides: large language models, prompt engineering, retrieval-augmented generation, AI agents, context windows, knowledge graphs, hallucinations, reasoning models, embeddings and the Model Context Protocol."),
    ("Do I need a technical background?", "No. The guides are beginner-friendly, with optional Go deeper sections for readers who want the technical detail."),
    ("In what order should I read the guides?", "In series order. Each part builds on the ones before it, starting with large language models."),
    ("Can I take the guides with me?", "Yes. Every guide has a Download the PDF button; enter your work email and we send it to your inbox."),
]
WF_FAQS = [
    ("What is an AI workflow in finance?", "A sequence of connected tasks used to complete a broader process. A good workflow has a defined task, the right inputs, a structured process, and an output that fits into the work that follows."),
    ("What are the five stages of a workflow?", "Task, context, process, output and review: define the job, gather context, run the process, produce the deliverable, and review the result."),
    ("Which workflows are in the library?", "Twenty workflows across earnings, company research, competition, and news and events, each with its stages, inputs and output."),
    ("Can I run these workflows in Pascal?", "Yes. Open any workflow and choose Try this workflow to see it run in Pascal."),
]


# ---------------------------------------------------------------- hub
def hub_page():
    c = counts()
    g, w, p = load("lib-glossary"), load("lib-workflows"), load("lib-prompts")
    hf, am = load(DESK[0][0]), load(DESK[1][0])
    llm, agents = load(FUND[0][0]), load(FUND[3][0])
    board = f"""<div class="fbd">
      <div class="fbd-col">
        <a class="fbd-c" href="/guides/{DESK[0][0]}"><span class="pill">Desk guide</span><p class="fbd-t">{hf["title"]}</p><p class="fbd-d">{hf["dek"]}</p></a>
        <a class="fbd-c" href="/guides/{DESK[1][0]}"><span class="pill">Desk guide</span><p class="fbd-t">{am["title"]}</p><p class="fbd-d">{am["dek"]}</p></a>
      </div>
      <div class="fbd-mid">
        <img src="/assets/shots/shot-research.webp" alt="Pascal researching across filings and an uploaded thesis" width="1600" height="844" decoding="async">
        <div class="fbd-ov"><p>Train your team with Pascal Academy.</p><a class="btn btn-mint" href="{SIGNUP}">Join a workshop</a></div>
      </div>
      <div class="fbd-col">
        <a class="fbd-c" href="/pascal-academy/guides/{FUND[0][0]}"><span class="pill pill-m">AI fundamentals</span><p class="fbd-t">{FUND[0][1]}</p><p class="fbd-d">{FUND[0][2]}</p></a>
        <a class="fbd-c" href="/pascal-academy/guides/{FUND[3][0]}"><span class="pill pill-m">AI fundamentals</span><p class="fbd-t">{FUND[3][1]}</p><p class="fbd-d">{FUND[3][2]}</p></a>
      </div>
    </div>"""
    t = tiles([
        ("Desk guides", "Guides for every investment desk", "Practical playbooks for hedge funds, asset managers, bankers, and private markets teams.", "#guides", "g-teal", "shot", DESK[0][3]),
        ("AI fundamentals", "AI fundamentals", "The core concepts behind AI, explained simply.", "#fundamentals", "g-mint", "chips", FUND_CHIPS["rag-retrieval-augmented-generation"]),
        ("AI glossary", "AI glossary", "An A-to-Z reference of AI terms written for investment teams.", "#glossary", "g-sea", "term", (g["groups"][0]["terms"][2]["term"], g["groups"][0]["terms"][2]["tag"], "")),
        ("Workflows", "Workflows", "Step-by-step ways to apply AI to real tasks.", "#workflows", "g-cream", "flow", w["cats"][0]["items"][0]["flow"][:4]),
        ("Prompts", "Prompt library", "Tested prompts for research, memos and modelling.", "#prompts", "g-deep", "code", p["items"][0]["prompt"][:150] + "…"),
        ("Agents", "Agent library", "Multi-step research agents for investment teams.", "#agents", "g-teal", "shot", ("shot-excel.webp", 1600, 504, "")),
    ])
    # rows
    glossary_cards = [card(f"/pascal-academy/ai-glossary#{slugify(x['name'])}",
                           thumb(grad(i + 2), "term", (x["terms"][0]["term"], x["terms"][0]["tag"], "")), esc(x["name"]),
                           "AI glossary", f"{len(x['terms'])} terms", esc(x["desc"]), attrs=" data-item") for i, x in enumerate(g["groups"])]
    wf_cards = [card(f"/pascal-academy/workflows#{slugify(cat['name'])}", thumb(grad(i + 3), "flow", cat["items"][0]["flow"][:4]),
                     esc(cat["name"]), "Workflows", f"{len(cat['items'])} workflow{'s' if len(cat['items']) != 1 else ''}", esc(cat["desc"]), attrs=" data-item")
                for i, cat in enumerate(w["cats"])]
    cats = []
    for it in p["items"]:
        if it["cat"] not in cats:
            cats.append(it["cat"])
    pr_cards = []
    for i, ct in enumerate(cats):
        first = next(x for x in p["items"] if x["cat"] == ct)
        n = sum(1 for x in p["items"] if x["cat"] == ct)
        pr_cards.append(card(f"/pascal-academy/prompt-library#{slugify(ct)}", thumb(grad(i + 4), "code", first["prompt"][:140] + "…"),
                             esc(ct), "Prompt library", f"{n} prompt{'s' if n != 1 else ''}", esc(first["title"]), attrs=" data-item"))
    ag = [("Generative Matrix", "Analysis", ("shot-agent-table.webp", 1600, 844, "Comparison table across companies with citations")),
          ("KPI Extractor", "Extraction", ("shot-excel.webp", 1600, 504, "Excel model with the KPI Extractor panel")),
          ("Research Memo Generator", "Generation", ("shot-word.webp", 1316, 660, "Research memo generated from a template"))]
    ag_cards = [card(f"/pascal-academy/agent-library#{slugify(n)}", thumb(grad(i), "shot", img), n, "Agent library", k, attrs=" data-item") for i, (n, k, img) in enumerate(ag)]
    meta = {"path": HUB, "title": "Pascal Academy: Learn AI for Institutional Finance",
            "description": "Practical AI education for investment teams: desk guides, AI fundamentals, a finance AI glossary, workflows, prompts and agents, plus live workshops.",
            "crumbs": [["Pascal Academy", HUB]], "og_kicker": "Pascal Academy", "og_title": "Learn AI for institutional finance",
            "llms": "Pascal Academy home: desk guides for hedge funds, asset managers, investment banks and private equity, a ten-part AI fundamentals series, an AI glossary for finance, workflows, prompts and agents.",
            "css": ["academy3.css"], "word_limit": 1800, "lead_max": 60, "priority": 0.8}
    sections = [
        grp("guides", "Desk guides", row([desk_card(i) for i in range(len(DESK))]), ("Go to all desk guides", "/guides"),
            "Practical playbooks for hedge funds, asset managers, bankers, and private markets teams."),
        grp("fundamentals", "AI fundamentals", row([fund_card(i) for i in range(len(FUND))]), ("Go to the series", "/pascal-academy/ai-fundamentals"),
            "The core concepts behind AI, explained simply."),
        grp("glossary", "AI glossary", row(glossary_cards), ("Go to the glossary", "/pascal-academy/ai-glossary"),
            "An A-to-Z reference of AI terms written for investment teams."),
        grp("workflows", "Workflows", row(wf_cards), ("Go to all workflows", "/pascal-academy/workflows"),
            "Step-by-step ways to apply AI to real tasks."),
        grp("prompts", "Prompt library", row(pr_cards), ("Go to all prompts", "/pascal-academy/prompt-library"),
            "Tested prompts for research, memos and modelling."),
        grp("agents", "Agent library", row(ag_cards), ("Go to the agents", "/pascal-academy/agent-library"),
            "Multi-step research agents for investment teams."),
    ]
    nav = side([("guides", "Desk guides"), ("fundamentals", "AI fundamentals"), ("glossary", "AI glossary"),
                ("workflows", "Workflows"), ("prompts", "Prompt library"), ("agents", "Agent library")], "Academy sections")
    return front(meta) + '<div class="ac">\n' + hero("Pascal", "Academy",
        "Pascal Academy is practical AI education for modern investment teams: guides for every desk, the core concepts explained simply, and tested workflows, prompts and agents.") + band(board + t) + f"""  <div class="bw" id="hub-results">
    {browse("Browse all resources.", "Search guides, concepts and tools", "#hub-results")}
    <div class="bw-g">
      {nav}
      <div class="bw-m">
        {"".join(sections)}
        <p class="ac-empty" hidden>Nothing matches that search. Try a broader term.</p>
      </div>
    </div>
  </div>
  {faq_block([(esc(q), esc(a)) for q, a in HUB_FAQS])}
  {workshop()}
</div>
</div>
""" + DEMO + SCRIPT


# ---------------------------------------------------------------- guides (desk + fundamentals)
def doc_page(slug):
    d = load(slug)
    desk = d["kind"] == "desk"
    m = mins(d["meta"])
    if desk:
        idx = [s for s, *_ in DESK].index(slug)
        seq = [(f"/guides/{s}", s, True, i) for i, (s, *_) in enumerate(DESK)]
        crumbs = [["Pascal Academy", HUB], ["Desk guides", "/guides"], [d["title"], d["path"]]]
        series = f"Desk guide {idx + 1} of {len(DESK)}"
        big = desk_thumb(idx, lazy=False, cls="th-hero")
    else:
        idx = [s for s, *_ in FUND].index(slug)
        seq = [(f"/pascal-academy/guides/{s}", s, False, i) for i, (s, *_) in enumerate(FUND)]
        crumbs = [["Pascal Academy", HUB], ["AI fundamentals", "/pascal-academy/ai-fundamentals"], [d["title"], d["path"]]]
        series = f"AI fundamentals · Part {idx + 1} of {len(FUND)}"
        big = fund_thumb(idx, cls="th-hero")
    parts = [p.strip().replace("~", "") for p in d["meta"].split("·") if p.strip() and p.strip() != "Pascal Academy"]
    updated = next((p for p in parts if p.startswith("Updated")), "")
    parts = [p for p in parts if not p.startswith("Updated")]
    upd = [b["h"] for b in d["about"] if b["t"] == "updated"]
    updated = (updated or ("Updated " + upd[0] if upd else "")).replace("Updated", "Last updated")
    chapters = d["chapters"]
    body = []
    if d["intro"]:
        body.append(f'<div class="ac-intro">{render_blocks(d["intro"])}</div>')
    for c in chapters:
        bl = render_blocks(c["blocks"])
        if re.match(r"further reading", c["h"], re.I):
            bl = link_guides(bl, slug)
        body.append(f'<section class="ac-sec" id="{esc(c["id"])}" aria-labelledby="{esc(c["id"])}-h"><h2 id="{esc(c["id"])}-h">{c["h"]}</h2>\n{bl}\n</section>')
    about = [b for b in d["about"] if b["t"] == "p"] + d["outro"]
    rel = RELATED.get(slug)
    rel_h = f'<p>See how this works in Pascal: <a href="{rel[0]}">{rel[1]}</a>.</p>' if rel else ""
    if about or rel:
        body.append(f'<aside class="ac-about"><p class="ac-about-h">About this guide</p>{render_blocks(about)}{rel_h}</aside>')
    faqs = d["faqs"] + [(esc(q), esc(a)) for q, a in EXTRA_FAQS.get(slug, [])]
    toc = "".join(f'<li><a href="#{esc(c["id"])}">{re.sub(r"<[^>]+>", "", c["h"])}</a></li>' for c in chapters)
    if faqs:
        toc += '<li><a href="#faq">Frequently asked questions</a></li>'
    # keep learning: the next two in the series plus one from the other track
    nxt = [seq[(idx + k) % len(seq)] for k in (1, 2)]
    kl = []
    for href, s, isdesk, i in nxt:
        if isdesk:
            kl.append(card(href, desk_thumb(i), load(s)["title"], "Desk guide", f'{mins(load(s)["meta"])} min read', h="h3"))
        else:
            kl.append(card(href, fund_thumb(i), esc(FUND[i][1]), f"Part {i + 1:02d}", f'{mins(load(s)["meta"])} min read', h="h3"))
    if desk:
        kl.append(card("/pascal-academy/ai-fundamentals", fund_thumb(0), "AI fundamentals", "Series", f"{len(FUND)} guides", h="h3"))
    else:
        kl.append(card(f"/guides/{DESK[0][0]}", desk_thumb(0), load(DESK[0][0])["title"], "Desk guide", f'{mins(load(DESK[0][0])["meta"])} min read', h="h3"))
    title, desc = SEO[slug]
    words = sum(len(re.sub(r"<[^>]+>", " ", x).split()) for x in body)
    meta = {"path": d["path"], "title": title, "description": desc, "crumbs": crumbs, "schema": "article",
            "name": d["title"], "og_kicker": "Pascal Academy", "og_title": d["title"] + (": " + d["dek"] if desk and len(d["dek"]) < 70 else ""),
            "llms": desc, "css": ["academy3.css"], "word_limit": max(2000, words + 900),
            "faq_min": min(4, len(faqs)), "lead_min": 8, "lead_max": 60, "priority": 0.7}
    if iso_date(updated):
        meta["updated"] = iso_date(updated)
    return front(meta) + f"""<div class="ac ac-doc">
<div class="rp" aria-hidden="true"><i></i></div>
<div class="frame">
  <header class="ah">
    <div class="ah-l">
      {{{{crumbs}}}}
      <p class="ah-k">{esc(updated) if updated else esc(series)}</p>
      <h1 class="ah-t">{d["title"]}</h1>
      <p class="lead">{d["dek"]}</p>
      <p class="ah-m">{" · ".join(esc(x) for x in parts)}</p>
      <div class="ah-by"><span class="ah-av"><img src="/assets/favicon.svg" alt="" width="40" height="40"></span><span><b>Pascal Academy</b><span>{esc(series)}</span></span></div>
      <div class="ah-a"><button class="btn btn-dark" type="button" data-gate-open>Download the PDF</button></div>
    </div>
    <div class="ah-r">{big}</div>
  </header>
  <div class="ag">
    <aside class="toc" aria-label="Table of contents">
      <div class="toc-in">
        <p class="toc-h">Table of contents</p>
        <div class="toc-track"><span class="toc-fill"></span><ol data-spy>{toc}</ol></div>
        <div class="toc-cta">
          <p class="toc-cta-t">Take this guide with you.</p>
          <p>Get the PDF in your inbox.</p>
          <button class="btn btn-dark" type="button" data-gate-open>Download the PDF</button>
        </div>
      </div>
    </aside>
    <article class="ac-prose" id="article">
      <details class="toc-m"><summary>Table of contents</summary><ol>{toc}</ol></details>
{chr(10).join(body)}
    </article>
  </div>
  {faq_block(faqs) if faqs else ""}
  <section class="kl" aria-labelledby="kl-h">
    <h2 class="sx-t" id="kl-h">Keep learning</h2>
    <div class="kl-g">{"".join(kl)}</div>
  </section>
  {workshop()}
</div>
</div>
""" + DEMO + gate(d["title"], slug, m) + SCRIPT


# ---------------------------------------------------------------- AI fundamentals index
def fund_index():
    c = counts()
    meta = {"path": "/pascal-academy/ai-fundamentals", "title": "AI Fundamentals for Finance | Pascal Academy",
            "description": "Build a practical understanding of modern AI concepts and how they apply to institutional finance, from LLMs and RAG to agents, embeddings and MCP.",
            "crumbs": [["Pascal Academy", HUB], ["AI fundamentals", "/pascal-academy/ai-fundamentals"]],
            "og_kicker": "Pascal Academy", "og_title": "AI fundamentals for institutional finance",
            "llms": "Index of the ten-part AI Fundamentals series: LLMs, prompt engineering, RAG, AI agents, context windows, knowledge graphs, hallucinations, reasoning models, embeddings and MCP.",
            "css": ["academy3.css"], "word_limit": 1300, "priority": 0.7}
    t = tiles([(f"Part {i + 1:02d}", esc(l), esc(dsc), f"/pascal-academy/guides/{s}", grad(i + 1), "chips", FUND_CHIPS[s])
               for i, (s, l, dsc) in enumerate(FUND[:5])], "Start the series")
    more = [card("/pascal-academy/workflows", thumb("g-cream", "flow", load("lib-workflows")["cats"][0]["items"][0]["flow"][:4]), "Workflows", "Library", "",
                 "How AI is applied across research, due diligence, modelling and investment workflows."),
            card("/pascal-academy/prompt-library", thumb("g-deep", "code", load("lib-prompts")["items"][0]["prompt"][:140] + "…"), "Prompt library", "Library", "",
                 "Browse tested prompts for institutional finance."),
            card("/pascal-academy/ai-glossary", thumb("g-sea", "term", (load("lib-glossary")["groups"][0]["terms"][2]["term"], "LLM", "")), "AI glossary", "Library", "",
                 "Explore AI terminology through an A-Z reference.")]
    return front(meta) + '<div class="ac">\n' + hero("AI", "Fundamentals",
        "Build a practical understanding of modern AI concepts and learn how they apply to institutional finance.",
        extra=f'<p class="hh-m">{len(FUND)} guides · {c["fund_min"]} min in total · Beginner-friendly with advanced sections</p>') + band(t) + f"""  <div class="bw" id="fund-results">
    {browse("Build the vocabulary.", "Search the series", "#fund-results")}
    <div class="bw-g bw-g-full">
      <div class="bw-m">
        <p class="sx-s sx-lead">Short explainers for the ideas that keep showing up in institutional AI work.</p>
        <div class="gg" data-group>{"".join(fund_card(i) for i in range(len(FUND)))}</div>
        <p class="ac-empty" hidden>Nothing matches that search.</p>
        {grp("more", "More from Pascal Academy", row(more))}
      </div>
    </div>
  </div>
  {faq_block([(esc(q), esc(a)) for q, a in FUND_FAQS])}
  {workshop()}
</div>
</div>
""" + DEMO + SCRIPT


# ---------------------------------------------------------------- glossary
def glossary_page():
    g = load("lib-glossary")
    n = sum(len(x["terms"]) for x in g["groups"])
    t = tiles([(esc(x["name"]), esc(x["name"]), esc(x["desc"]) + f" {len(x['terms'])} terms.", f"#{slugify(x['name'])}", grad(i + 2), "term",
                (x["terms"][0]["term"], x["terms"][0]["tag"], "")) for i, x in enumerate(g["groups"])], "Glossary themes")
    secs = []
    for gi, x in enumerate(g["groups"]):
        terms = "".join(f"""<article class="tm" id="{slugify(t_["term"])}" data-item>
            <span class="tm-bar {grad(gi + 2)}"></span>
            <div class="tm-h"><h4>{t_["term"]}</h4><span class="pill {grad(gi + 2)}-p">{esc(t_["tag"].upper() if len(t_["tag"]) <= 4 else t_["tag"].title())}</span></div>
            <p>{t_["def"]}</p></article>""" for t_ in x["terms"])
        secs.append(grp(slugify(x["name"]), esc(x["name"]), f'<div class="tms">{terms}</div>', sub=f'{esc(x["desc"])} {len(x["terms"])} terms.', h="h3"))
    meta = {"path": "/pascal-academy/ai-glossary", "title": "AI Glossary for Finance | Pascal Academy",
            "description": "A finance-focused reference of AI terms for investment teams, covering LLMs, RAG, agents, embeddings, MCP and governance, grouped by theme with search.",
            "crumbs": [["Pascal Academy", HUB], ["AI glossary", "/pascal-academy/ai-glossary"]],
            "og_kicker": "Pascal Academy", "og_title": "AI glossary for finance",
            "llms": f"A finance-focused glossary of {n} AI terms for investment teams, grouped into themes: models and foundations, core AI and agents, retrieval and knowledge, prompting, integration and platform, finance and governance.",
            "css": ["academy3.css"], "word_limit": 4400, "lead_min": 8, "priority": 0.7}
    return front(meta) + '<div class="ac">\n' + hero("AI", "Glossary", "An A-to-Z reference of AI terms written for investment teams.",
        extra='<p class="hh-m">Finance-focused definitions grouped by theme. For the longer explanations, read the <a href="/pascal-academy/ai-fundamentals">AI fundamentals</a> series.</p>') + band(t) + f"""  <div class="bw" id="gl-results">
    {browse(f"Browse all {n} terms.", "Search the glossary", "#gl-results")}
    <div class="bw-g">
      {side([(x["name"], x["name"]) for x in g["groups"]], "Glossary themes")}
      <div class="bw-m">
        <p class="sx-s sx-lead">Search or filter to find the terms that come up in research, modelling, and AI discussions.</p>
        {"".join(secs)}
        <p class="ac-empty" hidden>No term matches that search.</p>
      </div>
    </div>
  </div>
  {faq_block(g["faqs"])}
  {workshop()}
</div>
</div>
""" + DEMO + SCRIPT


# ---------------------------------------------------------------- workflows
def workflows_page():
    w = load("lib-workflows")
    n = sum(len(c["items"]) for c in w["cats"])
    t = tiles([(f'Stage {s["n"]}', esc(s["name"]) + ". " + esc(s["q"]), esc(s["d"]), None, grad(i), "", None)
               for i, s in enumerate(w["stages"])], "The anatomy of a workflow")
    secs = []
    k = 0
    for ci, c in enumerate(w["cats"]):
        items = []
        for it in c["items"]:
            steps = "".join(f"<li>{s}</li>" for s in it["steps"])
            inputs = "".join(f"<li>{i.strip()}</li>" for i in it["inputs"].split("·") if i.strip())
            items.append(f"""<details class="wf" id="{esc(it["id"])}" data-item>
            <summary>{thumb(grad(k), "flow", it["flow"])}<span class="gc-b"><span class="pill">{esc(c["name"])}</span><h4 class="gc-t">{it["title"]}</h4><span class="gc-d">{it["desc"]}</span><span class="wf-o">See how it works</span></span></summary>
            <div class="wf-b">
              <div><p class="wf-k">How it works</p><ol class="wf-st">{steps}</ol></div>
              <div><p class="wf-k">Inputs</p><ul class="wf-in">{inputs}</ul>
                <p class="wf-k">Output</p><p>{it["output"]}</p>
                <p><a class="btn btn-dark" href="{{{{demo_url}}}}">Try this workflow</a></p></div>
            </div>
          </details>""")
            k += 1
        secs.append(grp(slugify(c["name"]), esc(c["name"]), f'<div class="wfs">{"".join(items)}</div>',
                        sub=f'{esc(c["desc"])} {len(c["items"])} workflow{"s" if len(c["items"]) != 1 else ""}.', h="h3"))
    meta = {"path": "/pascal-academy/workflows", "title": "AI Workflows for Finance | Pascal Academy",
            "description": f"{n} step-by-step AI workflows for investment teams: earnings analysis, company research, peer comparison, bull and bear theses, news and events.",
            "crumbs": [["Pascal Academy", HUB], ["Workflows", "/pascal-academy/workflows"]],
            "og_kicker": "Pascal Academy", "og_title": "AI workflows for real financial work",
            "llms": f"{n} AI workflows for investment teams, each with its stages, inputs and output: earnings, company research, competition, news and events.",
            "css": ["academy3.css"], "word_limit": 3400, "priority": 0.7}
    return front(meta) + '<div class="ac">\n' + hero("AI", "Workflows",
        "How AI turns financial work into repeatable processes. See how real financial tasks can be broken down, automated, and run with AI.",
        extra='<p class="hh-m">Every workflow breaks a financial task into five stages: define the job, gather context, run the process, produce the deliverable, and review the result.</p>') + band(
        '<h2 class="fb-t">The anatomy of a workflow</h2>' + t, "fb-stages") + f"""  <div class="bw" id="wf-results">
    {browse(f"Browse all {n} workflows.", "Search workflows", "#wf-results")}
    <div class="bw-g">
      {side([(c["name"], c["name"]) for c in w["cats"]], "Workflow categories")}
      <div class="bw-m">
        <p class="sx-s sx-lead">Step-by-step workflows for the tasks analysts do every day. Each one shows the inputs, process, and deliverable. Use ready-made <a href="/pascal-academy/prompt-library">prompts</a> and <a href="/pascal-academy/agent-library">agents</a> for the same tasks.</p>
        {"".join(secs)}
        <p class="ac-empty" hidden>No workflow matches that search.</p>
      </div>
    </div>
  </div>
  {faq_block([(esc(q), esc(a)) for q, a in WF_FAQS])}
  {workshop()}
</div>
</div>
""" + DEMO + SCRIPT


# ---------------------------------------------------------------- prompts
def prompts_page():
    p = load("lib-prompts")
    cats = []
    for it in p["items"]:
        if it["cat"] not in cats:
            cats.append(it["cat"])
    t = tiles([(esc(x["k"]), esc(x["k"]), x["v"], None, grad(i), "", None) for i, x in enumerate(p["components"])], "What a finance prompt contains")
    secs = []
    k = 0
    for ci, c in enumerate(cats):
        cards = []
        for it in [x for x in p["items"] if x["cat"] == c]:
            cards.append(f"""<article class="pc" id="{slugify(it["title"])}" data-item>
            <div class="th th-code"><div class="th-bz"><div class="th-scr {grad(k)}"><div class="tcode"><span class="tcode-bar"><i></i><i></i><i></i><span>Prompt {it["n"]}</span></span><pre>{it["prompt"]}</pre></div></div></div></div>
            <div class="gc-b"><span class="pill">{esc(c)}</span><h4 class="gc-t">{it["title"]}</h4><p class="gc-d">{it["when"]}</p>
              <div class="pc-a"><button type="button" class="btn btn-dark btn-sm" data-copy>Copy prompt</button><button type="button" class="btn btn-line btn-sm" data-expand>Show full prompt</button></div></div>
          </article>""")
            k += 1
        secs.append(grp(slugify(c), esc(c), f'<div class="pcs">{"".join(cards)}</div>', sub=f'{len(cards)} prompt{"s" if len(cards) != 1 else ""}.', h="h3"))
    mistakes = [m for m in p["mistakes"] if not m["k"].lower().startswith("chain")]
    cot = next((m for m in p["mistakes"] if m["k"].lower().startswith("chain")), None)
    mis = "".join(f'<div class="mc"><span class="tm-bar {grad(i)}"></span><h3>{m["k"]}</h3><p>{m["v"]}</p></div>' for i, m in enumerate(mistakes))
    bounds = "".join(f'<div class="bd"><h3>{m["k"]}</h3><p>{m["v"]}</p></div>' for m in p["bounds"])
    meta = {"path": "/pascal-academy/prompt-library", "title": "AI Prompts for Finance | Pascal Academy",
            "description": f"{len(p['items'])} tested AI prompts for institutional finance: company research, earnings, modelling, comps, IC memos, portfolio and investor communication.",
            "crumbs": [["Pascal Academy", HUB], ["Prompt library", "/pascal-academy/prompt-library"]],
            "og_kicker": "Pascal Academy", "og_title": "Tested AI prompts for finance",
            "llms": f"{len(p['items'])} copy-ready AI prompts for investment teams, plus how to structure a finance prompt and when AI should not make the call.",
            "css": ["academy3.css"], "word_limit": 3600, "lead_min": 10, "priority": 0.7}
    return front(meta) + '<div class="ac">\n' + hero("AI", "Prompts", "Tested prompts for research, memos and modelling. Copy, adapt and run.",
        extra='<p class="hh-m"><b>Start with the task.</b> Each card contains a structured prompt you can copy and adapt to your workflow. Replace the bracketed fields with your company, data and specific requirements. Add the context the model needs, then specify the format you want in the output.</p>') + band(
        '<h2 class="fb-t">What makes a finance prompt effective</h2><p class="fb-s">Output quality reflects input quality. A prompt that produces a useful result for an investment task has a recognizable structure.</p>' + t, "fb-stages") + f"""  <div class="bw" id="pr-results">
    {browse(f"Browse all {len(p['items'])} prompts.", "Search prompts", "#pr-results")}
    <div class="bw-g">
      {side([(c, c) for c in cats], "Prompt categories")}
      <div class="bw-m">
        <p class="sx-s sx-lead">Filter by category or search by task. Each card includes a structured prompt you can copy and adapt for your workflow. The <a href="/pascal-academy/guides/prompt-engineering">prompt engineering guide</a> explains why these patterns work.</p>
        {"".join(secs)}
        <p class="ac-empty" hidden>No prompt matches that search.</p>
      </div>
    </div>
  </div>
  <section class="lx" aria-labelledby="mis-h">
    <h2 class="sx-t" id="mis-h">Common mistakes to avoid</h2>
    <div class="mcs">{mis}</div>
    {f'<aside class="ac-co ac-co-principle"><p class="ac-co-lab">{cot["k"]}</p><div class="ac-co-body"><p>{cot["v"]}</p></div></aside>' if cot else ""}
  </section>
  <section class="dk" aria-labelledby="bd-h">
    <div class="dk-in">
      <h2 class="dk-t" id="bd-h">When AI should not make the call.</h2>
      <p class="dk-s">AI accelerates the analytical process, but investment judgment stays with the analyst. There are specific scenarios where AI should not be relied on for final outputs or decisions.</p>
      <div class="bds">{bounds}</div>
    </div>
  </section>
  {faq_block(p["faqs"])}
  {workshop()}
</div>
</div>
""" + DEMO + SCRIPT


# ---------------------------------------------------------------- agents
def agents_page():
    src = (ROOT.parent.parent / "_academy_src/txt/pascal-academy_agent-library.txt").read_text()
    lines = src.splitlines()
    ans = [l[4:] for l in lines[lines.index("[h2] Frequently asked questions."):] if l.startswith("[p] ")]
    faqs = list(zip(load_agent_faq_questions(), ans))
    agents = [
        ("Analysis", "01", "Generative Matrix",
         "Filter companies, then analyze them using AI to answer your specific questions and get detailed insights across your filtered company set.",
         ["Select companies", "Define question", "Analyze", "Compare"], "Works with", ["Public companies", "Smart Search", "My Vault"],
         ("shot-agent-table.webp", 1600, 844, "Generative Matrix style output: a comparison table across companies with citations")),
        ("Extraction", "02", "KPI Extractor",
         "Automatically extract tables and graphs from company filings and your own documents into Excel. No more manual copy-paste.",
         ["Select company", "Select source", "Select period", "Extract"], "Sources", ["Annual Report", "Earnings Presentation", "Quarterly Report", "My Vault"],
         ("shot-excel.webp", 1600, 504, "Excel model with the Pascal KPI Extractor panel planning its steps")),
        ("Generation", "03", "Research Memo Generator",
         "Generate customized company research reports using your fund's template. No more hours of research, just a click.",
         ["Select sources", "Choose template", "Generate", "Review"], "Templates", ["Company Primer", "Earnings Analysis", "IPO Prospectus", "Credit Memo", "+ Custom"],
         ("shot-word.webp", 1316, 660, "Word research memo generated by Pascal from a template")),
    ]
    t = tiles([(cat, name, esc(desc), f"#{slugify(name)}", grad(i), "shot", img) for i, (cat, n, name, desc, *_r, img) in enumerate(agents)], "Agents")
    rows = []
    for i, (cat, n, name, desc, steps, klab, kv, img) in enumerate(agents):
        st = "".join(f"<li>{esc(s)}</li>" for s in steps)
        kvs = "".join(f"<li>{esc(x)}</li>" for x in kv)
        rows.append(f"""<section class="ar{" flip" if i % 2 else ""}" id="{slugify(name)}" aria-labelledby="{slugify(name)}-h">
      <div class="ar-c">
        <span class="pill">{cat} · {n}</span>
        <h3 class="ar-t" id="{slugify(name)}-h">{name}</h3>
        <p>{esc(desc)}</p>
        <ol class="wf-st wf-st-row">{st}</ol>
        <p class="wf-k">{klab}</p><ul class="wf-in">{kvs}</ul>
        <p><a class="btn btn-dark" href="{{{{demo_url}}}}">Run agent</a></p>
      </div>
      <div class="ar-m">{thumb(grad(i), "shot", img, cls="th-big")}</div>
    </section>""")
    why = [("Built for investment work", "Each agent is designed around a defined investment workflow, from screening and extraction to memo generation and portfolio monitoring."),
           ("Simple setup", "Select the companies, sources, and output format you need. The agent applies the workflow and produces a structured result."),
           ("Source-backed outputs", "Every output includes citations to the underlying sources, making facts, figures, and conclusions easy to trace and verify.")]
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
    why_c = "".join(f'<div class="mc"><span class="tm-bar {grad(i)}"></span><h3>{a}</h3><p>{esc(b)}</p></div>' for i, (a, b) in enumerate(why))
    how_c = "".join(f'<div class="bd"><span class="bd-k">{a}</span><h3>{b}</h3><p>{esc(c)}</p></div>' for a, b, c in how)
    tpl_c = [card(h, thumb(grad(i + 1), "chips", [("file-text", b), ("list-checks", "Sections"), ("quote", "Citations")]), b, f"Template {a}" if a != "+" else "Custom",
                  desc=esc(c)) for i, (a, b, c, h) in enumerate(tpl)]
    own_t = tiles([(f"Step {a}", b, esc(c), None, grad(i), "", None) for i, (a, b, c) in enumerate(own)], "Create an agent for your workflow")
    meta = {"path": "/pascal-academy/agent-library", "title": "AI Agents for Finance | Pascal Academy",
            "description": "Pascal's AI agents for institutional finance: screen company universes, extract KPIs from filings into Excel, and generate research memos from templates.",
            "crumbs": [["Pascal Academy", HUB], ["Agent library", "/pascal-academy/agent-library"]],
            "og_kicker": "Pascal Academy", "og_title": "AI agents for investment research",
            "llms": "Pascal's agent library: Generative Matrix (screen and analyse companies), KPI Extractor (filings to Excel), Research Memo Generator (template reports), with research templates and a framework for building your own agent.",
            "css": ["academy3.css"], "word_limit": 1800, "lead_min": 8, "priority": 0.7}
    return front(meta) + '<div class="ac">\n' + hero("AI", "Agents", "Purpose-built agents for institutional finance. Research, extract and generate.",
        extra=f'<p class="hh-m">Run repeatable finance workflows, from research to memo generation. Each agent handles a specific task and delivers a structured output. For the concepts behind them, read <a href="/pascal-academy/guides/ai-agents">AI agents explained</a>.</p>') + band(
        '<h2 class="fb-t">Agents for investment research</h2>' + t) + f"""  <section class="lx" aria-labelledby="why-h">
    <h2 class="sx-t" id="why-h">Agents built around how investment teams actually work.</h2>
    <div class="mcs mcs-3">{why_c}</div>
  </section>
  <div class="ars">{"".join(rows)}</div>
  <section class="dk" aria-labelledby="how-h">
    <div class="dk-in">
      <h2 class="dk-t" id="how-h">Build for the task.</h2>
      <p class="dk-s">Every Pascal agent follows the same pattern. You define what you need, the agent gathers and processes the inputs, and you get a structured output with citations back to the source.</p>
      <div class="bds bds-3">{how_c}</div>
    </div>
  </section>
  <section class="lx" aria-labelledby="tpl-h">
    <div class="sx-h"><div><h2 class="sx-t" id="tpl-h">Pre-built templates for common research outputs.</h2>
      <p class="sx-s">The Research Memo Generator comes with templates designed for the outputs investment teams produce regularly. Each defines the structure, sections, and data points the agent should populate. You can also build your own from scratch.</p></div></div>
    <div class="gg">{"".join(tpl_c)}</div>
  </section>
  <section class="fb fb-stages fb-inline" aria-labelledby="own-h"><div class="fb-in">
    <h2 class="fb-t" id="own-h">Create an agent for your workflow.</h2>
    <p class="fb-s">The agents above cover common tasks, but every investment team has workflows specific to how they work. Start with a task you repeat every week and turn it into a reusable agent. The <a href="/pascal-academy/workflows">workflow library</a> shows the same five stages applied to real tasks.</p>
    {own_t}
  </div></section>
  {faq_block(faqs)}
  {workshop()}
</div>
</div>
""" + DEMO + SCRIPT


def load_agent_faq_questions():
    from bs4 import BeautifulSoup
    s = BeautifulSoup((ROOT.parent.parent / "_academy_src/pascal-academy_agent-library.html").read_text(), "html.parser")
    out = []
    for b in s.find("main").find_all("button", attrs={"aria-expanded": True}):
        q = " ".join(b.get_text(" ").replace("+", " ").split())
        if q.endswith("?"):
            out.append(esc(q).replace("&#x27;", "'"))
    return out


# ---------------------------------------------------------------- workshop sign-up
def signup_page():
    meta = {"path": SIGNUP, "title": "Join Pascal Academy: Team AI Workshops",
            "description": "Sign up for Pascal Academy workshops. Train your investment team on practical AI workflows, planned around your firm by the Pascal team.",
            "crumbs": [["Pascal Academy", HUB], ["Sign up", SIGNUP]], "og_kicker": "Pascal Academy",
            "og_title": "Train your team with Pascal Academy", "llms": "Sign-up form for Pascal Academy team workshops.",
            "css": ["academy3.css"], "word_limit": 700, "faq_min": 0, "lead_min": 10, "noindex": True, "priority": 0.5}
    opts = lambda xs: '<option value="">Select…</option>' + "".join(f"<option>{x}</option>" for x in xs)
    codes = [("+1", "United States"), ("+44", "United Kingdom"), ("+91", "India"), ("+65", "Singapore"), ("+971", "United Arab Emirates"),
             ("+852", "Hong Kong"), ("+61", "Australia"), ("+49", "Germany"), ("+33", "France"), ("+81", "Japan")]
    code_opts = "".join(f'<option value="{c}" data-country="{n}">{n} ({c})</option>' for c, n in codes)
    form = f"""<div class="su">
      <div class="su-l">
        <h2 class="fb-t">Tell us about your team</h2>
        <p class="fb-s">We'll follow up to plan a workshop tailored to your firm. Sessions draw on the <a href="/guides">desk guides</a>, the <a href="/pascal-academy/ai-fundamentals">AI fundamentals</a> series and the <a href="/pascal-academy/workflows">workflows</a>, <a href="/pascal-academy/prompt-library">prompts</a> and <a href="/pascal-academy/agent-library">agents</a> in the library.</p>
        {thumb("g-teal", "shot", ("shot-research.webp", 1600, 844, "Pascal researching across filings and an uploaded thesis"), cls="th-big")}
      </div>
      <div class="su-r">
      <form class="ac-form" data-signup-form novalidate>
        <label>Full name *<input name="name" autocomplete="name" required></label>
        <label>Work email *<input name="email" type="email" autocomplete="email" required></label>
        <label>Organization *<input name="organization" autocomplete="organization" required></label>
        <div class="ac-form-2">
          <label>Team size *<select name="teamSize" required>{opts(["1–5", "6–20", "21–50", "51–200", "200+"])}</select></label>
          <label>Focus area<select name="focus">{opts(["Hedge Funds", "Asset &amp; Wealth Management", "Banks &amp; Financial Institutions", "Asset Servicing", "Private Equity &amp; Private Credit", "Corporate Treasury &amp; Hedge Accounting", "Other"])}</select></label>
        </div>
        <label>Phone <span class="ac-opt">(optional)</span><span class="ac-phone"><select name="countryCode" aria-label="Country code">{code_opts}</select><input name="phone" type="tel" autocomplete="tel-national" inputmode="tel"></span></label>
        <p class="ac-gate-err" role="alert" hidden></p>
        <button class="btn btn-dark" type="submit">Sign up</button>
        <p class="ac-gate-fine">By submitting, you agree to be contacted about Pascal Academy.</p>
      </form>
      <div class="ac-gate-done ac-form-done" hidden>
        <span class="ac-gate-ok">{I("check")}</span>
        <h2>Thank you.</h2>
        <p>The Pascal team will reach out to plan a program for your organization.</p>
        <a class="btn btn-line" href="{HUB}">Back to Academy</a>
      </div>
      </div>
    </div>"""
    return front(meta) + '<div class="ac">\n' + hero("Train your team with", "Pascal Academy",
        "Learn how to apply AI across your team's day-to-day investment workflows.") + band(form, "fb-form") + "</div>\n</div>\n" + DEMO + SCRIPT


# ---------------------------------------------------------------- desk guides index (/guides)
def desk_index():
    meta = {"path": "/guides", "title": "AI Desk Guides for Investment Teams | Pascal Academy",
            "description": "Practical AI playbooks for hedge funds, asset managers, investment banks and private equity: use cases, workflows, benefits and implementation.",
            "crumbs": [["Pascal Academy", HUB], ["Desk guides", "/guides"]], "og_kicker": "Pascal Academy",
            "og_title": "Guides for every investment desk",
            "llms": "Index of Pascal Academy desk guides: AI for hedge funds, asset management, investment banking and private equity.",
            "css": ["academy3.css"], "word_limit": 900, "priority": 0.7}
    t = tiles([("Desk guide", load(s)["title"], esc(desc), f"/guides/{s}", grad(i), "shot", img) for i, (s, l, desc, img, panel) in enumerate(DESK)], "Desk guides")
    total = sum(mins(load(s)["meta"]) or 0 for s, *_ in DESK)
    more = [card("/pascal-academy/ai-fundamentals", fund_thumb(0), "AI fundamentals", "Series", f"{len(FUND)} guides", "The core concepts behind AI, explained simply."),
            card("/pascal-academy/workflows", thumb("g-cream", "flow", load("lib-workflows")["cats"][0]["items"][0]["flow"][:4]), "Workflows", "Library", "",
                 "Step-by-step ways to apply AI to real tasks."),
            card("/pascal-academy/prompt-library", thumb("g-deep", "code", load("lib-prompts")["items"][0]["prompt"][:140] + "…"), "Prompt library", "Library", "",
                 "Tested prompts for research, memos and modelling.")]
    return front(meta) + '<div class="ac">\n' + hero("Desk", "Guides",
        "Practical playbooks for hedge funds, asset managers, bankers, and private markets teams.",
        extra=f'<p class="hh-m">{len(DESK)} guides · {total} min in total</p>') + band(t) + f"""  <div class="bw" id="dg-results">
    {browse("Browse all desk guides.", "Search the desk guides", "#dg-results")}
    <div class="bw-g bw-g-full">
      <div class="bw-m">
        <div class="gg gg-2" data-group>{"".join(desk_card(i) for i in range(len(DESK)))}</div>
        <p class="ac-empty" hidden>Nothing matches that search.</p>
        {grp("more", "More from Pascal Academy", row(more))}
      </div>
    </div>
  </div>
  {faq_block([(esc(q), esc(a)) for q, a in DESK_FAQS])}
  {workshop()}
</div>
</div>
""" + DEMO + SCRIPT


# ---------------------------------------------------------------- main
def main():
    STAGING.mkdir(exist_ok=True)
    for f in STAGING.glob("*.html"):
        f.unlink()
    pages = {"academy-hub": hub_page(), "academy-fundamentals": fund_index(), "academy-glossary": glossary_page(),
             "academy-workflows": workflows_page(), "academy-prompts": prompts_page(), "academy-agents": agents_page(),
             "academy-signup": signup_page(), "academy-desk-guides": desk_index()}
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
