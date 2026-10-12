#!/usr/bin/env python3
"""How much of a draft's copy made it onto a built page.

    python3 _build/coverage.py ~/Downloads/pascal_page_x.html ask-pascal-x

Prints the % of the draft's sentences (6+ words) found on the page, the draft sentences that are missing, and
draft section headlines (kicker -> headline) that are missing.
"""
import html, os, re, sys

def lines(s):
    s = re.sub(r'<style.*?</style>|<script.*?</script>|<svg.*?</svg>|<h2 class="sr-only">.*?</h2>', '', s, flags=re.S)
    out = [re.sub(r'\s+', ' ', html.unescape(x)).strip() for x in re.split(r'<[^>]+>', s)]
    return [x for x in out if x]

norm = lambda x: re.sub(r'[^a-z0-9 ]', '', x.lower().replace('’', "'"))

draft = lines(open(os.path.expanduser(sys.argv[1])).read())
page_src = open(os.path.join(os.path.dirname(__file__), 'pages', sys.argv[2] + '.html')).read()
page_src = re.sub(r'<!--#include[^>]*?title="([^"]*)"[^>]*?sub="([^"]*)"[^>]*-->', r'<p>\1</p><p>\2</p>', page_src)
page = norm(' '.join(lines(page_src)))
sents = [x for x in draft if len(x.split()) >= 6]
missing = [x for x in sents if norm(x)[:45] not in page]
print(f"coverage: {len(sents) - len(missing)}/{len(sents)} = {100 * (len(sents) - len(missing)) // max(1, len(sents))}%")
for m in missing:
    print("  missing:", m[:140])
for i in range(len(draft) - 1):
    k, h = draft[i], draft[i + 1]
    if 1 <= len(k.split()) <= 5 and not k.endswith('.') and h.endswith('.') and 3 <= len(h.split()) <= 14 and k[0].isupper():
        if norm(h)[:30] not in page:
            print(f"  missing section: {k} -> {h}")
