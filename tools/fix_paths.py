import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
html_files = list(root.rglob('*.html'))
patterns = [
    (re.compile(r'href=\"/(plugins/)', re.IGNORECASE), r'href="\1'),
    (re.compile(r'href=\"/(css/)', re.IGNORECASE), r'href="\1'),
    (re.compile(r'src=\"/(plugins/)', re.IGNORECASE), r'src="\1'),
    (re.compile(r'src=\"/(js/)', re.IGNORECASE), r'src="\1'),
    (re.compile(r'src=\"/(images/)', re.IGNORECASE), r'src="\1'),
    (re.compile(r'url\(\'/images/', re.IGNORECASE), r"url('images/"),
    (re.compile(r'url\(\"/images/', re.IGNORECASE), r'url("images/'),
    (re.compile(r'link rel=\"shortcut icon\" href=\"/images/', re.IGNORECASE), r'link rel="shortcut icon" href="images/'),
    (re.compile(r'link rel=\"icon\" href=\"/images/', re.IGNORECASE), r'link rel="icon" href="images/'),
]

changed = []
for path in html_files:
    text = path.read_text(encoding='utf-8')
    orig = text
    for pat, repl in patterns:
        text = pat.sub(repl, text)
    if text != orig:
        path.write_text(text, encoding='utf-8')
        changed.append(str(path.relative_to(root)))

print(f"Updated {len(changed)} files")
for f in changed:
    print(f)
