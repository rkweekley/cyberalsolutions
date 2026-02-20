#!/usr/bin/env python3
"""
Normalize 'Read more' anchors:
- If an anchor has duplicate aria-labels, keep the more specific one.
- If an anchor has only generic aria-label="Read more" or no aria-label, attempt to find the nearest preceding <h3> title and set aria-label="Read more: {title}".
"""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
files = list(root.rglob('*.html'))
updated = 0
for p in files:
    try:
        s = p.read_text(encoding='utf-8')
    except Exception:
        continue
    orig = s
    # collapse duplicate aria-labels where a generic one precedes a specific one
    s = re.sub(r'aria-label="Read more"\s+aria-label="Read more: ([^"]+)"', r'aria-label="Read more: \1"', s)
    # find all anchors with inner text 'Read more' (case-sensitive)
    def repl(m):
        tag = m.group(0)
        # if already has aria-label with colon 'Read more:' leave it
        if 'aria-label="Read more:' in tag:
            return tag
        # if has aria-label="Read more" we'll replace it later by finding heading
        # find position in the file
        start = m.start()
        # find nearest preceding <h3 ...>...</h3>
        before = s[:start]
        h3s = list(re.finditer(r'<h3[^>]*>(.*?)</h3>', before, flags=re.S|re.I))
        title = None
        if h3s:
            title = h3s[-1].group(1)
            # strip HTML tags
            title = re.sub(r'<[^>]+>', '', title).strip()
        if not title:
            # fallback to generic
            title = 'post'
        # remove existing aria-label if generic
        new_tag = re.sub(r'aria-label="[^"]*"', '', tag)
        # inject aria-label
        new_tag = new_tag.replace('>Read more<', f' aria-label="Read more: {title}">Read more<')
        return new_tag

    s = re.sub(r'<a[^>]*>\s*Read more\s*</a>', repl, s)
    if s != orig:
        p.write_text(s, encoding='utf-8')
        updated += 1
print(f"Normalized 'Read more' in {updated} files")
