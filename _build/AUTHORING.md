# Authoring a page for Pascal website v2 (rev 2: enterprise redesign)

The design copies Glean and Atlan: restrained type, hairline-framed grid, mono labels, **real product
screenshots** on gradient panels, very little copy. Colours are Pascal's.

**Read both templates fully before writing; copy their structure and class usage exactly:**
- `_build/pages/platform.html`: product/hub template (Atlan dark hero → Glean body)
- `_build/pages/solutions-asset-management.html`: solutions template (Glean split hero)

## Build (parallel-safe)
```
cd /Users/diyathakur/Documents/Claude/website-v2
python3 _build/build.py --only <name>[,<name2>]
```
Zero ❌ required. Never run without `--only`. Preview: http://localhost:4610/<path>. Do NOT edit site.css,
build.py, icons.py or partials. Page CSS (rarely needed) goes in `_build/static/assets/pages/<name>.css`, listed
in front matter `"css"`, every selector scoped under a page class. Delete any page CSS file from the previous
version that you no longer use and remove it from front matter.

## Hard rules (the build enforces the first three)
1. **Word budget**: ≤ 600 words outside the FAQ (hubs may set `"word_limit": 750`). Aim for 350–500.
   Glean's product pages are ~450 words. If in doubt, cut.
2. **Hero lead**: one `<p class="lead">`, 12–40 words, answer-first ("X is … It …").
3. **4 FAQs** (`details.faq-item`), answers 1–2 short sentences.
4. **Headlines** are short and two-tone: `Statement. <span class="mute">Continuation.</span>` (h2), or in
   dark heroes `<span class="accent">…</span>`. ≤ 10 words. No question headlines.
5. **Feature paragraphs** ≤ 30 words. One per feature row. No bullet lists inside feature rows.
6. **Visuals = real screenshots** from `/assets/shots/` (catalogue below) inside
   `<div class="panel[ panel-dark| panel-cream]"><div class="shot"><img …></div></div>`.
   Only build an HTML `.ui` mockup when no screenshot fits, and keep it to ≤ 5 short rows (see platform.html f3).
7. **Never use "X, not Y" contrasts** ("Built like an investor thinks. Not a pile of files.", "…, not just …", "rather than", "instead of"). The build fails headings that use them. State what Pascal does, plainly.
8. **No AI-template tells**: no "What is X?" sections, no "Why it matters", no "How it works" step essays,
   no "The problem" sections, no stacked triads of adjectives, no em dashes, no exclamation marks.
   Banned words: delve, robust, landscape, seamless, cutting-edge, revolutionize, unlock, game-changer,
   leverage (verb), empower, supercharge, effortless, harness.
9. **Facts**: keep only facts already in the old page / drafts. Don't invent numbers, customers or quotes.
   List anything a human must verify in your final message.

## Page skeletons

**Product / capability page** (most pages):
```
<section class="hero-a" …> {{crumbs}} .badge h1.display(with .accent) p.lead .actions .hero-media>.shot(img) </section>
  — OR for capability pages, Glean split hero: <div class="frame"><section class="hero-g">…copy… / .hero-g-media>.panel>.shot</section></div>
<div class="frame">
  optional: <section class="cells"> 3 × .cell(.stat-num + .stat-lbl)  — only real numbers
  2–4 × <section class="row split[ flip]"> .split-copy(eyebrow "01 Label", h2 two-tone, p ≤30 words, .link) + .split-media(.panel>.shot)
  optional: <section class="row row-pad"> .checks table (4–6 rows, ✓ {{icon:check}} / {{icon:minus}}) — hubs only
  <section class="row"> related: .row-pad-sm h2 + .cells.row with 3 × a.cell (n, b, span, span.link)
  <section class="row row-pad bg-cream" id="faq"> .faq-wrap …
</div>
<!--#include demo-band title="Short line." sub="Short line."-->
```

**Solutions page**: copy solutions-asset-management.html section for section: hero-g → subnav → overview head + 3 stats →
operating model (`.om` with 3 vertical tabs + screenshot panels) → dark capabilities `.caps` (icon + title only,
`data-planned` links) → `<!--#include tech-section-->` → impact `.stories` (4 × eyebrow + h3 ≤ 12 words + metric) +
optional real quote → FAQ → demo band.

## Screenshot catalogue (`/assets/shots/`, all WebP; use exact width/height in the img tag)
| File | W×H | Shows |
|---|---|---|
| shot-ask.webp | 1600×844 | Ask Pascal home: "Ask, Discover and Research" prompt box with Company / Source / Workflows / Filings / Web / Auto / Explore |
| shot-research.webp | 1600×844 | Research in progress: Searching / Reviewing steps over filings and an uploaded thesis (Honeywell) |
| shot-citations.webp | 1600×844 | Answer with numbered citations; source presentation open at page 4 of 5 beside it (Honeywell) |
| shot-sources.webp | 1600×843 | Select Source panel: integrations (SharePoint, Outlook, Teams, IC memos, broker reports, expert calls…) + My Vault |
| shot-agent-run.webp | 1369×960 | Event Brief workflow for Sea running: steps searching Teams chats, broker research, expert calls |
| shot-agent-table.webp | 1600×844 | Agent output: "Street vs management framing" table for Sea Limited with citations |
| shot-workflows.webp | 1600×843 | Workflow library grid with the Event Brief workflow dialog open (Run Workflow) |
| shot-excel.webp | 1600×504 | Excel model (FY20A–FY25A income statement) with the Pascal KPI Extractor panel planning steps |
| shot-ppt.webp | 1270×585 | PowerPoint slide generated by Pascal: "Gross Margin Expansion Story" |
| shot-word.webp | 1316×660 | Word document generated by Pascal: "Growth, Constraints & Forward Debate" |
| shot-office-chat.webp | 1600×694 | Pascal chat after generating an idea-pitch deck, with the file ready to download |
| shot-altdata.webp | 1600×844 | Alternative Data: Macro Pulse indicators with monthly sparklines |
| shot-intel.webp | 1600×844 | Pascal Intel: X digest for $PLTR with trackers and themes |

Hero `.hero-media` shots: first image on the page, no `loading="lazy"`. All others lazy.

## Site map
/platform · /platform/context-graph · /platform/institutional-memory · /platform/mcp-apis ·
/ask-pascal · /ask-pascal/cited-research · /ask-pascal/screeners · /ask-pascal/pascal-intel · /ask-pascal/alternative-data ·
/pascal-agents · /pascal-agents/workflow-library · /pascal-agents/autonomous-agents · /pascal-agents/decision-traces · /pascal-agents/office-suite ·
/solutions/asset-management · /solutions/hedge-funds · /solutions/private-markets · /solutions/investment-banking ·
(live) / · /security · /about · /news · /careers · /pascal-academy
