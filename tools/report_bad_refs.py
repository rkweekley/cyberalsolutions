#!/usr/bin/env python3
import os, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ASSET_DIRS = ['plugins/','css/','images/','js/','fonts/']
pattern = re.compile(r'(?:href|src)=["\'](?P<path>[^"\']+)["\']')

problems = []
for root,dirs,files in os.walk(ROOT):
    for fn in files:
        if not fn.lower().endswith('.html'):
            continue
        fp = os.path.join(root, fn)
        rel = os.path.relpath(fp, ROOT)
        with open(fp,'r',encoding='utf-8') as f:
            data = f.read()
        for m in pattern.finditer(data):
            p = m.group('path')
            if p.startswith(('http://','https://','//','/','../')):
                continue
            for d in ASSET_DIRS:
                if p.startswith(d):
                    problems.append((rel,p))

if not problems:
    print('No problematic asset refs found.')
else:
    print('Files with asset refs missing ../ or absolute path:')
    for f,p in problems:
        print(f, '->', p)
