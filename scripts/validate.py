"""Validate the daily HTML publication without external dependencies."""
import datetime
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
day = datetime.date.fromisoformat(sys.argv[1]).isoformat()
page = root / 'archive' / f'{day}.html'
text = page.read_text()
assert (root / 'index.html').read_bytes() == page.read_bytes(), 'Homepage differs from daily archive'

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = 0
        self.links = []
        self.stack = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.items += tag == 'div' and attrs.get('class') == 'item'
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:
            self.stack.append(tag)
    def handle_endtag(self, tag):
        assert self.stack and self.stack.pop() == tag, f'Unbalanced HTML: {tag}'

p = Page()
p.feed(text)
assert not p.stack, 'Unclosed HTML tags'
assert 15 <= p.items <= 20, f'Expected 15–20 items, got {p.items}'
assert re.search(r'全(\d+)本', text).group(1) == str(p.items), 'Metadata count mismatch'
assert not re.search(r'[가-힯]', text), 'Unexpected Hangul characters'
d = datetime.date.fromisoformat(day)
label = f'{d.year}年{d.month}月{d.day}日({"月火水木金土日"[d.weekday()]})'
assert f'<title>Trend Digest — {label}</title>' in text, 'Title date mismatch'
assert f'<div class="date">{label}</div>' in text, 'Displayed date mismatch'
assert all(u.startswith(('https://','/archive/')) for u in p.links), 'Invalid link'
listing = (root / 'archive/index.html').read_text()
links = re.findall(r'href="(/archive/\d{4}-\d{2}-\d{2}\.html)"', listing)
assert len(links) == len(set(links)), 'Duplicate archive links'
assert links[0] == f'/archive/{day}.html', 'Newest issue is not first'
assert all((root / link.lstrip('/')).is_file() for link in links), 'Broken archive link'
print(f'PASS: {day}, {p.items} articles, balanced HTML, dates, homepage, {len(links)} archive links')
