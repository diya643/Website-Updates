# Pascal AI — website v2

The new pascalailabs.com: homepage, product, industry, security, Pascal Academy and founder's notes pages. A static, SEO/GEO-first build in the Pascal teal design system.

| | |
|---|---|
| **Pages** | 44: homepage, 12 product pages, 7 industry pages, security, founder's notes and 22 Pascal Academy pages (including the 4 desk guides) |
| **Source** | `_build/pages/*.html` (one file per page) |
| **Output** | `public/` (what ships) |
| **Build** | `python3 _build/build.py` (requires Python 3.9+ and Pillow for OG images) |
| **Preview** | `python3 _build/serve.py` → http://localhost:4610/ · hosted preview: https://pascal-product-preview.vercel.app |
| **Ship** | see `INTEGRATION.md` |
| **SEO/GEO** | see `SEO-GEO-CHECKLIST.md`; the build audits every page and writes `_build/report.md` |
| **Fact-check** | see `VERIFY.md` before go-live |
| **Writing a page** | see `_build/AUTHORING.md` |

The build generates per page: meta title/description, canonical, Open Graph + Twitter tags, a 1200×630 OG image,
JSON-LD (`Organization`, `WebSite`, `WebPage`, `BreadcrumbList`, `SoftwareApplication` or `Service`, `FAQPage`),
plus site-wide `sitemap.xml`, `robots.txt`, `llms.txt`, `vercel.json` and `next.config.snippet.js`.
