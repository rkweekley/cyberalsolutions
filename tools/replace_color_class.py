#!/usr/bin/env python3
from pathlib import Path
root = Path(__file__).resolve().parents[1]
count = 0
for p in root.rglob('*.html'):
    try:
        s = p.read_text(encoding='utf-8')
    except Exception:
        continue
    if 'class="color"' in s:
        s2 = s.replace('class="color"', 'class="text-primary"')
        p.write_text(s2, encoding='utf-8')
        count += 1
print(f"Replaced 'class=\"color\"' in {count} files")
