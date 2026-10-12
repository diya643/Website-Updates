import sys
from bs4 import BeautifulSoup, NavigableString
def walk(el,d,out):
    for c in el.children:
        if isinstance(c,NavigableString):
            t=' '.join(c.split())
            if t: out.append('  '*d+repr(t[:110]))
        else:
            a=' '.join(f'{k}={v}' for k,v in c.attrs.items())
            kids=[x for x in c.children if not (isinstance(x,NavigableString) and not x.strip())]
            if c.name in ('div','span') and not a and len(kids)==1:
                walk(c,d,out); continue
            out.append('  '*d+f'<{c.name}{" "+a if a else ""}>')
            walk(c,d+1,out)
s=BeautifulSoup(open(sys.argv[1]).read(),'html.parser'); out=[]; walk(s,0,out)
a=int(sys.argv[2]) if len(sys.argv)>2 else 0; b=int(sys.argv[3]) if len(sys.argv)>3 else len(out)
print('\n'.join(out[a:b]))
