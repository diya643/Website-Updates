# October 2026 restructure — shared brief for page builders

> **Update 7 Oct (later):** case studies and all /case-studies URLs are removed; Industries pages have no stat strip; Generative Office Suite is retired; Pascal Data Agent is one page at /pascal-agents/data-agent (anchors #vault-viewer, #classifier, #extraction); /solutions/investment-banking is a live page again; the nav says Industries; essays live at /news/founders-notes; floating cards sit under windows (never over content) and capability cards no longer flip. `build.py` SITE_PAGES is the source of truth for valid paths.

Source: the website review call with the founder (Vibhav) and sales lead (Vikrant), 5 Oct 2026.
This file is the single source of truth for every builder. Read it fully before you touch a page.

## How the site is built
- Static build: `cd ~/Documents/Claude/website-v2/_build && python3 build.py --only <file1>,<file2>` (page file names without `.html`).
  Always use `--only` with your own files; never run a full build (other builders work in parallel).
- Pages: `_build/pages/*.html`, each starts with a `<!--meta {json}-->` front matter (path, title ≤60 chars,
  description 120–160 chars, crumbs, schema "software" | "solution", name, og_kicker, og_title, llms, priority,
  optional "css": ["file.css"], "word_limit"). Look at `pages/solutions-hedge-funds.html` (the reference page) and the other existing pages.
- Includes: `<!--#include name k="v"-->` pulls `partials/name.html` and swaps `{{k}}`.
- Tokens: `{{icon:name}}`, `{{icon:name:cls}}`, `{{logo:name}}`, `{{demo_url}}`, `{{crumbs}}`.
  Icons: see `icons.py` PATHS. Logos: see `logos.py` (SRC + INLINE). Unknown names fail the build.
- Page CSS: put page-specific CSS in `static/assets/pages/<your-file>.css` and list it in the meta "css" array.
  **Do not edit `static/assets/site.css`, `site.js`, `nav.html`, `footer.html` or `build.py`.** If you need a shared change, say so in your final report.
- The audit (in `build.py`) fails the build on: title/description length, not exactly one H1, heading level jumps,
  fewer than 3 contextual internal links in `<main>`, fewer than 4 FAQs, hero `<p class="lead">` under 12 words,
  banned words, "X, not Y" in headings, broken internal links, and the word budget (default 600 words outside the FAQ;
  anything between `<!--mock-->` and `<!--/mock-->` is product UI and is excluded).
- Local preview server is already running at http://localhost:4610. Screenshots:
  `python3 ~/Documents/Claude/website-v2/_tools/snap.py /path 1440 [css-selector|-] [name]` → `_tools/shots/<name>.png`.
  Player scenes: `python3 ~/Documents/Claude/website-v2/_tools/scenes.py /path` → `_tools/shots/ucp-*.png`.
  Check 1440, 1100 and 375 widths. Look at your screenshots with the Read tool and fix anything ugly, clipped or misaligned.

## Valid internal paths (link only to these, or the live pages /about /security /news /careers /pascal-academy)
/platform · /platform/context-graph · /platform/mcp-apis
/ask-pascal · /ask-pascal/decision-traces · /ask-pascal/cited-research · /ask-pascal/screeners · /ask-pascal/pascal-intel
/pascal-agents · /pascal-agents/autonomous-agents · /pascal-agents/workflow-library · /pascal-agents/office-suite
/data-agent · /data-agent/vault-viewer · /data-agent/classifier · /data-agent/extraction
/solutions/asset-wealth-management · /solutions/asset-servicing · /solutions/hedge-funds · /solutions/private-equity-credit
/solutions/banking · /solutions/treasury-hedge-accounting · /solutions/ai-transformation
/case-studies · /case-studies/hedge-funds · /case-studies/asset-management · /case-studies/asset-servicing · /case-studies/banking · /case-studies/treasury
/research
Retired (redirected, never link): /platform/institutional-memory, /ask-pascal/alternative-data, /solutions/asset-management,
/solutions/private-markets, /solutions/investment-banking. Their old sources are in `_build/retired/` for reference.

## Writing rules (hard)
- Pascal writing ban list (build fails): delve, underscore, landscape, robust, game-changer, seamless, unlock, transformative,
  groundbreaking, cutting-edge, revolutionize, empower, embark, synergy, holistic, streamline, unpack, deep dive, moreover,
  furthermore, leverage(s/d/ing), "in today's world", "rapidly evolving", "it's worth noting".
- **Never write "X, not Y" contrast constructions**: no "not just", "rather than", "instead of", ", not …", ". Not …".
  State what Pascal does, positively.
- Enterprise tone: plain, specific, short sentences. Nothing that reads AI-generated (no rule-of-three filler,
  no "Imagine…", no rhetorical questions in body copy, no em-dash chains). British spelling as on the rest of the site (summarise, organise).
- Only one CTA type on the site: "Book a demo" → `{{demo_url}}`. No secondary CTAs (no "Talk to sales", "Get started").
- FAQ heading is always exactly "Frequently asked questions". FAQs must be specific to the page (do not reuse another page's set).
- **Numbers:** every stat strip uses page-specific numbers (the founder said the 40% / 95% / 85% strip was overdone; it now
  stays only on /platform). The user has approved illustrative numbers for this preview. Make them plausible and specific
  to the page, never round-number marketing fluff. List every number you invent in your final report so it can go into VERIFY.md.
- **No customer names, no people's names.** Logos and named clients come later. Case studies are anonymised
  ("Global long/short equity fund", "Large Indian asset manager"). No real employee names; roles only.
- Real public companies may appear inside product mockups (NVIDIA, TSMC, Sea Limited, Honeywell…) with figures marked illustrative.
- Organisation rule: never include customer PII.

## Positioning decisions from the call
- Industries (Solutions) are now: Asset & wealth management · Asset servicing · Hedge funds · Private equity & credit ·
  Banking · Treasury & hedge accounting, plus AI transformation (by initiative). Stick to financial services (plus corporate treasury).
- Every Solutions page is organised **front office / middle office / back office**, each with its own persona and a ~30-second
  looping product walkthrough (the "GIF"), and each industry must read differently: different use cases, different numbers,
  different FAQs, different hero line. The founder pointed at Hebbia for "different use cases across asset types".
- Industry definitions: **front office** = research, portfolio management, deal teams, client-facing (personas: analyst, PM, CIO,
  deal team, banker). **Middle office** = trading workflows, trade support and confirmations, reconciliations, P&L and exposure,
  collateral and margin, risk, valuations (personas: head of trading, COO, CRO; CTO cuts across). **Back office** = DDQ/RFP,
  fund accounting and administration, investor reporting, regulatory reporting, KYC, compliance (persona: COO, CFO, CCO, head of IR).
- Index & ETF was copied from a competitor; it is removed everywhere.
- Context graph and institutional memory are one product now ("the memory lives in the graph"): page /platform/context-graph,
  nav label "Context graph & memory". Connectors feed the graph and every thesis. Decisions enter the graph from meeting notes
  (e.g. a team decides the weekly review moves from Monday to Tuesday; any agent now knows it) and from reviewer edits (e.g. DDQ answers).
- MCP & APIs has three value propositions, in this order: (1) bring your graph and context into any LLM through MCP
  (the most important), (2) orchestrate across many MCPs (your context + public filings + CapIQ etc. through Pascal),
  (3) expose Pascal workflows over MCP or API (e.g. run a "guidance vs actuals" workflow as a slash command inside Claude). Plus one headline stat.
- **Pascal Data Agent** (new product family, /data-agent): Pascal turns messy internal files (broker PDFs, expert-call
  transcripts, internal notes, emails) into structured, entity-tagged data. It classifies document types, extracts entities
  and fields (company, ticker, sector, broker, rating, price target, PT change, expert relationship, stance, conviction),
  keeps provenance to the page, respects permissions, and serves the result two ways: a **Vault viewer** for analysts
  (File Explorer with AI: filter by type, company, sector, date 7/30/90 days, broker; open a document at the section about your
  company; "why this is tagged"), and **MCP** for agents (`list_documents`, `get_document`). Example asks: "show me every NDA",
  "every Goldman Sachs note on NVDA in the last 30 days". This is "the most valuable part… shit a foundation model cannot do":
  vertical entities (speaker names, company names, brokers), scattered sources. It also answers the question customers keep
  asking, "are you a data company?": Pascal is a data platform for your own research, the way Snowflake is a data platform.
  References the founder named: Scale AI (annotation of data), Reducto (parse / extract / classify / studio / table editor), ModelML.
  Alternative data is removed; the classifier replaces it.
- Pascal Agents should show many more agents (the founder: "putting just 3, 4 is not very useful, we are doing so many more things").
- Generative Office Suite stays, with low emphasis.
- Case studies get their own nav tab with one page per industry, each one detailed end-to-end story: what the firm was
  struggling with, exactly what Pascal did step by step, results, and what came next.

## Shared components you should use
- **Use-case player** (the 30-second GIF stand-in). Copy the markup pattern from `pages/solutions-hedge-funds.html`:
  `<!--#include ucp-open crumb="Pascal Agents" title="Event brief" label="30-second walkthrough: …"-->`
  then 5 `<div class="ucp-scene" data-label="Trigger">…</div>` scenes (6 s each by default; `data-dur="5000"` to change),
  then `<!--#include ucp-close-->`. Inside scenes use `.pui-*` kit parts plus: `.ucp-in` (fades in, delay with `style="--d:.6s"`),
  `.ucp-type` (types a single line), `.ucp-bar` (progress bar, `--w:87%`), `<!--#include ucp-tick d="1.4s"-->` (spinner → tick),
  `.ucp-trigger` (event card with logo), `.ucp-big` (big number), `.ucp-cap` (green status line), `.ucp-cols` (2 columns).
  Stage height is 344px: keep each scene to what fits (about 5 rows or a 4-row table). Write illustrative but realistic content.
- Office tabs: `.om` / `.om-list` / `.om-tab` with `<small class="om-who"><b>For</b>Persona · Persona</small>` and `.om-media` panels.
- Case-study teaser: `.cs-teaser` / `.cs-teaser-copy` / `.cs-teaser-nums` (see the reference page).
- Persona strip: `.who` with three `<div><p class="eyebrow">…</p><b>…</b><p>…</p></div>`.
- Stat strip: `<div class="cells row">` with `.cell` → `.stat-num` (+ `<small>` unit) and `.stat-lbl`.
- Product UI kit `.pui` (see `site.css` "Pascal product UI kit" and existing `partials/ui-*.html`). Wrap mockups in `<!--mock-->…<!--/mock-->`.
- Flip capability cards `.caps` / `.cap.flip` (dark section), technology band `<!--#include tech-section-->`, `<!--#include demo-band title="…" sub="…"-->`.

## Quality bar
Glean / Atlan enterprise look in Pascal teal. Hairline-framed grid, restrained type, real product UI (no stock icons as heroes,
no gradients-as-content, no emoji). Every visual must look like a real screen of the product. Check your pages at 1440, 1100 and 375 px;
no horizontal scroll, nothing clipped, no overlapping text. Your final report: files changed, every invented number, anything you
could not resolve.
