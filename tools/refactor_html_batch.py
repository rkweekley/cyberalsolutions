#!/usr/bin/env python3
"""
Batch refactor HTML files: fix nested paragraphs, update color spans, add role to articles, and add aria-label to read-more buttons.
"""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
html_files = list(root.rglob('*.html'))
updated = 0
for p in html_files:
    try:
        text = p.read_text(encoding='utf-8')
    except Exception:
        continue
    orig = text
    # fix nested paragraphs
    text = text.replace('<p><p>', '<div class="excerpt"><p>')
    text = text.replace('</p></p>', '</p></div>')
    # replace class color with text-primary
    text = text.replace('class="color"', 'class="text-primary"')
    # add role="article" to article tags that don't have role
    text = re.sub(r'<article((?![^>]*role=)[^>]*?)>', r'<article role="article"\1>', text)
    # add aria-label to read-more links where missing
    text = re.sub(r'<a([^>]*class="[^"]*btn[^"]*")[^>]*href="([^"]+)"\s*>\s*Read more\s*</a>', r'<a \1 href="\2" aria-label="Read more" >Read more</a>', text)
    if text != orig:
        p.write_text(text, encoding='utf-8')
        updated += 1
print(f"Updated {updated} HTML files")
