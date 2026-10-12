"""Strip the live Next.js academy HTML down to bare semantic HTML (no classes) for inspection/extraction."""
import sys, re
from bs4 import BeautifulSoup, NavigableString, Comment
KEEP = {'section','article','header','nav','aside','h1','h2','h3','h4','h5','p','ul','ol','li','table','thead','tbody','tr','th','td',
        'a','strong','em','b','i','code','pre','blockquote','details','summary','button','span','div','br','hr','img','figure','figcaption','dl','dt','dd'}
def simp(el):
    for c in el.find_all(string=lambda s: isinstance(s, Comment)): c.extract()
    for t in el(['script','style','svg','noscript','iframe']): t.decompose()
    for t in el.find_all(True):
        if t.name not in KEEP: t.unwrap(); continue
        keep = {k: v for k, v in t.attrs.items() if k in ('id','href','aria-expanded','src','alt')}
        t.attrs = keep
    return el
if __name__ == '__main__':
    s = BeautifulSoup(open(sys.argv[1]).read(), 'html.parser')
    m = s.find('main') or s.body
    print(simp(m).prettify())
