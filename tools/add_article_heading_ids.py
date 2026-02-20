#!/usr/bin/env python3
"""
Add missing heading ids to <h3> within <article> blocks and ensure <article aria-labelledby> references them.
Also update 'Read more' links to include aria-label with the post title when possible.
"""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
files = list(root.rglob('*.html'))
updated = 0
for p in files:
    try:
        text = p.read_text(encoding='utf-8')
    except Exception:
        continue
    orig = text
    # iterate over article blocks
    def repl_article(match):
        article = match.group(0)
        # if article already has aria-labelledby, skip
        if 'aria-labelledby' in article:
            return article
        # find first h3 inside
        h3m = re.search(r'<h3( [^>]*)?>(.*?)</h3>', article, flags=re.S|re.I)
        if not h3m:
            return article
        h3_attrs = h3m.group(1) or ''
        h3_text = re.sub('<[^<]+?>', '', h3m.group(2)).strip()
        if not h3_text:
            return article
        # generate id
        safe = re.sub(r"[^a-z0-9]+", '-', h3_text.lower()).strip('-')
        id_candidate = f"{safe}-heading"
        # ensure unique within article by appending number if duplicate
        count = 1
        new_id = id_candidate
        while re.search(r'id="' + re.escape(new_id) + r'"', article):
            count += 1
            new_id = f"{id_candidate}-{count}"
        # add id to h3 tag
        new_h3 = f'<h3 id="{new_id}"{h3_attrs}>{h3m.group(2)}</h3>'
        article = article[:h3m.start()] + new_h3 + article[h3m.end():]
        # add aria-labelledby to article tag
        article = re.sub(r'<article', f'<article aria-labelledby="{new_id}"', article, count=1)
        # update Read more link aria-label if present and generic
        article = re.sub(r'<a([^>]*class="[^"]*btn[^"]*"[^>]*)>\s*Read more\s*</a>',
                         lambda m: f'<a{m.group(1)} aria-label="Read more: {h3_text}">Read more</a>', article)
        return article

    text = re.sub(r'<article[\s\S]*?</article>', repl_article, text, flags=re.I)
    if text != orig:
        p.write_text(text, encoding='utf-8')
        updated += 1
print(f"Processed {len(files)} files; updated {updated} files")
