#!/usr/bin/env python3
"""Fix asset references in HTML files by adding correct ../ prefix based on file depth.

Runs in-place edits for href/src values that start with known asset directories
like plugins/, css/, images/, js/, plugins/, and do not already start with ../ or / or http.
"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ASSET_DIRS = ['plugins/', 'css/', 'images/', 'js/', 'fonts/']

pattern = re.compile(r'(?P<attr>(?:href|src))=(?P<quote>["\'])(?P<path>[^"\']+)(?P=quote)')

def normalize_path_for_file(path, depth):
    # leave external and absolute paths alone
    if path.startswith(('http://', 'https://', '//', '/')):
        return path
    # strip any existing leading ../ segments
    stripped = re.sub(r'^(?:\.\./)+', '', path)
    # if the stripped path starts with an asset dir, compute correct prefix
    for d in ASSET_DIRS:
        if stripped.startswith(d):
            prefix = '../' * depth
            return prefix + stripped
    # otherwise leave unchanged
    return path

def fix_file(path):
    rel = os.path.relpath(path, ROOT)
    dirname = os.path.dirname(rel)
    # compute depth as number of path components in the dirname
    depth = len(dirname.split(os.sep)) if dirname else 0
    prefix = '../' * depth
    changed = False
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()

    def repl(m):
        p = m.group('path')
        newp = normalize_path_for_file(p, depth)
        if newp != p:
            nonlocal_changed[0] = True
            return f"{m.group('attr')}={m.group('quote')}{newp}{m.group('quote')}"
        return m.group(0)

    nonlocal_changed = [False]
    newdata = pattern.sub(repl, data)
    if nonlocal_changed[0]:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(newdata)
        return True
    return False

def main():
    updated = []
    for root, dirs, files in os.walk(ROOT):
        for fn in files:
            if not fn.lower().endswith('.html'):
                continue
            fp = os.path.join(root, fn)
            if fix_file(fp):
                updated.append(os.path.relpath(fp, ROOT))
    print('Updated {} files'.format(len(updated)))
    for u in updated:
        print('-', u)

if __name__ == '__main__':
    main()
