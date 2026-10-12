# SEO / GEO checklist — Pascal website v2

`[auto]` = generated or enforced by `_build/build.py` on every build. `[page]` = written into each page source.
`[launch]` = a one-time action when the pages go live.

## A. Site-wide

### Rendering & crawlability
- [x] [auto] Every page is static HTML; all copy is in the source (no JS needed to read it)
- [x] [auto] Clean folder URLs, no trailing slash, matching the live site (`/solutions/hedge-funds`)
- [x] [auto] `vercel.json`: `cleanUrls`, `trailingSlash: false`, 301 redirects (`/product` → `/platform`)
- [x] [auto] `sitemap.xml` with every indexable page + `lastmod`
- [x] [auto] `robots.txt` allows search + AI crawlers (GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended, Applebot-Extended, Bingbot…) and points at the sitemap
- [x] [auto] `llms.txt` at the root: what Pascal is + every page with a one-line description
- [x] [auto] Custom `404.html` (noindex)

### Entity & brand signals
- [x] [auto] `Organization` JSON-LD on every page (name, logo, url, `sameAs` LinkedIn + X)
- [x] [auto] `WebSite` JSON-LD
- [x] [page] Consistent entity names: Pascal AI, Ask Pascal, Pascal Agents, context graph, institutional memory

### Performance & UX
- [x] [auto] Fonts preconnected with `display=swap`; one shared CSS + one deferred JS file; assets cached 1 year
- [x] [page] Images have explicit width/height; below-the-fold images lazy-load
- [x] [page] Mobile layout to 375px; AA contrast; keyboard-accessible menus, tabs and FAQs; skip link
- [x] [auto] Favicon (SVG + apple-touch-icon), `theme-color`
- [x] [auto] Content visible without JavaScript (reveal animations only apply when JS runs)

### Launch
- [ ] [launch] Merge `public/` into the Next.js repo (see `INTEGRATION.md`) and deploy on Vercel
- [x] [launch] `DEMO_URL` points at https://pascalailabs.com/demo
- [ ] [launch] Google Search Console: submit `https://pascalailabs.com/sitemap.xml`, URL-inspect key pages, Request indexing
- [ ] [launch] Bing Webmaster Tools: submit sitemap (feeds ChatGPT search / Copilot)
- [ ] [launch] Validate 3+ pages in Google Rich Results Test and Schema.org validator
- [ ] [launch] Lighthouse on 3+ pages: SEO 100, Accessibility ≥ 95, Performance ≥ 90
- [ ] [launch] Fact-check every item in `VERIFY.md`

## B. Every page

### Head
- [x] [auto] `<title>` ≤ 60 chars, primary query first, ends `| Pascal AI` (audit fails otherwise)
- [x] [auto] Meta description 120–160 chars (audit fails otherwise)
- [x] [auto] Absolute canonical URL
- [x] [auto] Open Graph + Twitter tags with a unique 1200×630 OG image per page
- [x] [auto] `lang="en"`, viewport, `robots: index, follow, max-snippet:-1, max-image-preview:large`
- [x] [auto] Any element marked `data-placeholder` forces `noindex` until it's filled

### Structure
- [x] [auto] Exactly one H1, with the product label inside it so it carries the primary query; no skipped heading levels (audit fails otherwise)
- [x] [auto] Visible breadcrumb + `BreadcrumbList` schema that match the URL
- [x] [page] Semantic landmarks: `header`, `nav`, `main`, `section`, `article`, `footer`

### GEO content patterns
- [x] [page] Answer-first summary in the hero lede (40–70 words, "X is… It… so…")
- [x] [page] Definitional sentences for key concepts
- [x] [page] Comparison checklist `<table>` on the hub pages (Platform, Ask Pascal, Pascal Agents)
- [x] [auto] Word budget: ≤ 600 words outside the FAQ (hubs 750); hero lead 12–40 words. The build fails otherwise
- [x] [page] Specific, checkable facts (document types, systems, numbers) instead of vague claims
- [x] [page] 4–6 FAQs phrased as real queries, visible on page → `FAQPage` schema generated from them
- [x] [auto] Visible "Last updated" date + `dateModified` in schema

### Structured data
- [x] [auto] `Organization`, `WebSite`, `WebPage`, `BreadcrumbList` on every page
- [x] [auto] Product pages: `SoftwareApplication`; Solutions pages: `Service` with `audience`
- [x] [auto] `FAQPage` mirroring the visible FAQs exactly

### Linking & media
- [x] [auto] ≥ 3 contextual internal links in `<main>`; no broken internal links (audit fails otherwise)
- [x] [page] Hub ↔ spoke ↔ solutions linking; descriptive anchor text (audit warns on "learn more")
- [x] [auto] Every `<img>` has `alt` (audit fails otherwise); meaningful mockups have `role="img"` + `aria-label`
- [x] [auto] Links to capability pages that don't exist yet render as plain cards (no 404s) until the page is built

### Before shipping
- [ ] [page] No placeholder text; `VERIFY.md` items confirmed
- [x] [auto] Page is in `sitemap.xml` and `llms.txt`
