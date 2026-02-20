#!/usr/bin/env python3
"""Unify shared header/footer into partials and remove duplicate mobile-menu includes."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]

HEADER_PLACEHOLDER = '<div data-include="/partials/header.html"></div>'
FOOTER_PLACEHOLDER = '<div data-include="/partials/footer.html"></div>'
INCLUDE_SCRIPT = '  <script src="/js/include-partials.js" defer></script>\n'

HEADER_RE = re.compile(r'<header\b[^>]*>.*?</header>', re.IGNORECASE | re.DOTALL)
FOOTER_RE = re.compile(r'<footer\b[^>]*>.*?</footer>', re.IGNORECASE | re.DOTALL)
MOBILE_MENU_RE = re.compile(r'\s*<script[^>]*mobile-menu\.js[^>]*></script>\s*', re.IGNORECASE)

updated = 0
for path in root.rglob('*.html'):
    if 'partials' in path.parts:
        continue
    try:
        text = path.read_text(encoding='utf-8')
    except Exception:
        continue

    original = text

    headers = list(HEADER_RE.finditer(text))
    if headers:
        # Remove any extra headers beyond the first.
        for match in reversed(headers[1:]):
            text = text[:match.start()] + '' + text[match.end():]
        text = HEADER_RE.sub(HEADER_PLACEHOLDER, text, count=1)

    footers = list(FOOTER_RE.finditer(text))
    if footers:
        # Remove any extra footers before the last.
        for match in reversed(footers[:-1]):
            text = text[:match.start()] + '' + text[match.end():]
        # Replace the last footer with a placeholder.
        last_footer = list(FOOTER_RE.finditer(text))[-1]
        text = text[:last_footer.start()] + FOOTER_PLACEHOLDER + text[last_footer.end():]

    # Remove direct mobile-menu script includes; footer partial handles this.
    text = MOBILE_MENU_RE.sub('\n', text)

    # Ensure include-partials script is in the head.
    if 'include-partials.js' not in text and '</head>' in text:
        text = text.replace('</head>', INCLUDE_SCRIPT + '</head>')

    # Clean up the tags page leftover navbar fragment from the old template.
    if path.parts[-2:] == ('tags', 'index.html'):
        text = re.sub(
            r'(?s)\s*data-target="#navigation".*?<!-- Start Blog Section -->',
            '\n<!-- Start Blog Section -->',
            text,
        )

    if text != original:
        path.write_text(text, encoding='utf-8')
        updated += 1

print(f'Updated {updated} HTML files.')
