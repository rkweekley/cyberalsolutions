import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
html_files = list(root.rglob('*.html'))
asset_patterns = [
    re.compile(r'href="(css/[^"]+)"', re.IGNORECASE),
    re.compile(r'href="(plugins/[^"]+)"', re.IGNORECASE),
    re.compile(r'src="(js/[^"]+)"', re.IGNORECASE),
    re.compile(r'src="(plugins/[^"]+)"', re.IGNORECASE),
    re.compile(r'src="(images/[^"]+)"', re.IGNORECASE),
    re.compile(r'url\(["\']?(images/[^)"\']+)["\']?\)', re.IGNORECASE),
]

missing = {}
for html in html_files:
    text = html.read_text(encoding='utf-8')
    for pat in asset_patterns:
        for m in pat.findall(text):
            asset_path = root / m
            if not asset_path.exists():
                missing.setdefault(str(html.relative_to(root)), set()).add(m)

print(f"Checked {len(html_files)} HTML files")
if not missing:
    print("No missing assets found")
else:
    total = sum(len(v) for v in missing.values())
    print(f"Missing {total} assets in {len(missing)} files:")
    for html, assets in missing.items():
        print(f"- {html}:")
        for a in sorted(assets):
            print(f"    {a}")
