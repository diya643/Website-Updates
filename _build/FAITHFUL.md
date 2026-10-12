# Rebuilding a product page faithfully from its draft

The user's instruction: **"ALL has to be similar to the document."** Each product page must reproduce its draft
(the HTML file in ~/Downloads linked from the user's doc) section for section, in the same order, with the same copy
and the same mockups — rebuilt in the v2 design system. The previous version of every page cut the drafts down to
2–30% of their copy. That was wrong. Do not summarise, shorten, merge, reorder, rename or "improve" sections.

## Reference implementation — read it first
`_build/pages/ask-pascal-decision-traces.html` + `_build/static/assets/pages/decision-traces.css` is a faithful
rebuild of `~/Downloads/pascal_page_decision_traces_v3.html`. Match that approach exactly:
- every draft section → one `<section class="row split[ flip]">` (alternate sides), eyebrow = the draft's kicker,
  `<h2 class="h2">` = the draft's headline (put the second half in `<span class="mute">` where it reads naturally),
  `<p>` = the draft's paragraph **verbatim**, link = the draft's link text if it had one
- every draft mockup → rebuilt as clean HTML UI inside `.panel fit` (or `.panel-cream fit` / `.panel-dark fit`),
  with the draft's exact labels, values, statuses and names, styled in a page-scoped CSS file
- draft comparison tables → a real `<table>` with the draft's rows verbatim (see `.dt-compare`)
- draft "How it works / How it compounds / steps" → `.cells` with the draft's step labels and lines verbatim
- draft FAQ → the FAQ section verbatim (`details.faq-item`). If the draft has fewer than 4 FAQs, add one
  definitional question first ("What is <thing>?") answered from the draft's own hero copy
- draft "Related" cards → the related `.cells` row with the draft's labels and lines
- draft closing band → `<!--#include demo-band title="<draft closing headline>" sub="<draft closing subline>"-->`

## The ONLY permitted changes to the draft
1. **Pascal writing ban list** (the build enforces most of it):
   - words: delve, underscore (verb), landscape, robust, game-changer, seamless, leverage (verb), unlock,
     transformative, groundbreaking, cutting-edge, revolutionize, empower, navigate (metaphorical), embark,
     synergy, holistic, streamline, unpack, deep dive, it's important to note, it's worth mentioning,
     in today's world, in the age of AI, rapidly evolving, moreover, furthermore, it's worth noting
   - phrases: "This is not X, this is Y" and **trailing contrast fragments** ("Hand off the whole task, not just
     the question." / "A working spreadsheet, not a pasted table." / "…, not just the market's.").
     Rephrase ONLY the offending clause, keeping the rest of the line, e.g.
     "Hand off the whole task, not just the question." → "Hand off the whole task."
     "A working spreadsheet, not a pasted table." → "A working spreadsheet, every number sourced."
     The build fails headings that contain ", not", ". Not", "not just", "rather than", "instead of".
2. **Drop** the drafts' "Latest from Pascal" resource blocks and "[Client quote …] / [Name] · [Role]" placeholders
   (those articles and quotes don't exist).
3. **Hero** uses the light split hero `hero-g` (copy left, visual right) like every other page: crumbs from the
   existing front matter, the label inside the H1 (`<span class="h1-k"><span class="eyebrow">…</span></span>`),
   the draft's H1 and the draft's hero paragraph verbatim as `<p class="lead">` (long is fine), the draft's
   buttons (`btn-dark` "Book a demo" + the draft's secondary button as `btn-line`, pointing at an on-page anchor),
   and the draft's hero mockup on the right.
4. Draft stat strips → `.cells` with the draft's numbers and labels verbatim — unless the per-page overrides below
   say otherwise.
5. Real customer/firm names in mockups that look like real private firms → a fictional name; public companies
   (Honeywell, Sea, Amazon, NVIDIA, Palantir…) stay as in the draft.
6. No em dashes added; keep the draft's own punctuation otherwise.

## Mechanics
- Edit the existing page file in place. **Keep its front matter** (path, title, description, crumbs, schema, name,
  og_*, llms). Add `"word_limit": 3000, "lead_max": 120` and `"css": ["<page>.css"]` if you add page CSS.
- Page CSS: `_build/static/assets/pages/<page>.css`, every selector scoped under a page class on the frames
  (e.g. `<div class="frame pg-intel">`). Reuse classes from decision-traces.css by copying them into your file
  under your own scope if useful. Do NOT edit site.css, build.py, icons.py or partials.
- Build: `python3 _build/build.py --only <name>[,<name>]` → zero ❌.
- **Self-check coverage before finishing** (must be ≥ 90% unless the gap is only dropped resources/quotes and
  ban-list rephrasings — list those):
  ```
  python3 _build/coverage.py <draft-file-in-Downloads> <page-name>
  ```
- Visually check at 1440px and 375px (http://localhost:4610/<path>, or a headless browser if the pane is busy).

Final message: per page — build status, coverage %, the exact lines you changed from the draft and why
(ban-list / dropped placeholder / override), and any facts a human should verify.
