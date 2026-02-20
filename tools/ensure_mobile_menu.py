#!/usr/bin/env python3
"""
Ensure /js/mobile-menu.js is included in all HTML files under the project.
Inserts <script src="/js/mobile-menu.js"></script> before </body> if missing.
"""
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
count = 0
for p in root.rglob('*.html'):
    try:
        text = p.read_text(encoding='utf-8')
    except Exception:
        continue
    if 'mobile-menu.js' in text:
        continue
    if '</body>' not in text:
        continue
    new_text = text.replace('</body>', '  <script src="/js/mobile-menu.js"></script>\n</body>')
    p.write_text(new_text, encoding='utf-8')
    count += 1
print(f"Updated {count} HTML files to include /js/mobile-menu.js")
