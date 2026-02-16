#!/usr/bin/env python3
import re
from pathlib import Path
import os

root = Path.cwd()
html_files = list(root.rglob('*.html'))
href_re = re.compile(r'href="(/[^"\s]*)"')

modified = []

for p in html_files:
    text = p.read_text(encoding='utf-8')
    changed = False

    def repl(m):
        href = m.group(1)  # with leading /
        # skip protocol-relative or external
        if href.startswith('//'):
            return m.group(0)
        if len(href) > 1 and href[1] in ('#', '?'):
            return m.group(0)

        target = href.lstrip('/')
        if target == '':
            candidate = root / 'index.html'
        else:
            candidate = root / target
            if candidate.is_dir() or candidate.suffix == '':
                candidate = candidate / 'index.html'

        rel = os.path.relpath(candidate, start=p.parent)
        rel = rel.replace(os.path.sep, '/')
        nonlocal_changed = True
        return f'href="{rel}"'

    # perform replacement with a wrapper to track changes
    out = text
    for m in href_re.finditer(text):
        old = m.group(0)
        href = m.group(1)
        if href.startswith('//'):
            continue
        if len(href) > 1 and href[1] in ('#', '?'):
            continue
        target = href.lstrip('/')
        if target == '':
            candidate = root / 'index.html'
        else:
            candidate = root / target
            if candidate.is_dir() or candidate.suffix == '':
                candidate = candidate / 'index.html'
        rel = os.path.relpath(candidate, start=p.parent).replace(os.path.sep, '/')
        new = f'href="{rel}"'
        if old != new:
            out = out.replace(old, new)
            changed = True

    if changed:
        p.write_text(out, encoding='utf-8')
        modified.append(str(p.relative_to(root)))

print(f"Processed {len(html_files)} HTML files.")
if modified:
    print(f"Updated {len(modified)} files:")
    for m in modified:
        print(m)
else:
    print("No navigation hrefs needed updating.")
