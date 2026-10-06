#!/usr/bin/env python3
"""
SEO guard for cyberalsolutions.com — runs on every PR and push to master.

Exists because the homepage "Latest Posts" widget was a hand-maintained JS array
that silently went stale, so new blog posts never appeared on the homepage. Static
sites have no build step to keep derived lists in sync, so this check is the
substitute: it fails the build when a derived list drifts from its source.

Each failure prints exactly what to change. No dependencies beyond stdlib.
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
errors = []


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8", errors="ignore")


def check_homepage_matches_blog_index():
    """The homepage must show the same newest-3 posts, in the same order, as /blog/."""
    def card_links(html, scope_after=None):
        if scope_after:
            i = html.find(scope_after)
            html = html[i:] if i != -1 else html
        return [m.group(1) for m in re.finditer(r'<h3[^>]*>\s*<a\s+href="(/blog/[^"]+)"', html, re.S)]

    blog = read("blog/index.html")
    home = read("index.html")
    index_three = card_links(blog)[:3]
    home_block = home[home.find('id="home-blog-items"'):home.find('id="home-blog-items"') + 6000]
    home_three = card_links(home_block)[:3]

    if not home_three:
        errors.append("homepage: no post cards found in #home-blog-items")
        return
    if index_three != home_three:
        errors.append(
            "homepage 'Latest Posts' is out of sync with /blog/.\n"
            f"      /blog/ newest three: {index_three}\n"
            f"      homepage showing  : {home_three}\n"
            "      Fix: update the three static <article> cards inside #home-blog-items "
            "in index.html to match the top three cards on blog/index.html."
        )


def check_no_orphan_posts():
    """Every blog post must be reachable from an index page."""
    posts = sorted(p.name for p in (ROOT / "blog").glob("*.html") if p.name != "index.html")
    reachable = read("blog/index.html")
    p2 = ROOT / "blog/page/2/index.html"
    if p2.exists():
        reachable += read("blog/page/2/index.html")
    orphans = [p for p in posts if p not in reachable]
    if orphans:
        errors.append(
            f"{len(orphans)} blog post(s) exist but are linked from nowhere: {orphans}\n"
            "      Fix: add a card for each to blog/index.html (newest first) or blog/page/2/index.html."
        )


def check_sitemap():
    sm = read("sitemap.xml")
    try:
        root = ET.fromstring(sm)
    except ET.ParseError as e:
        errors.append(f"sitemap.xml does not parse: {e}")
        return
    children = list(root)
    if any(c.tag != f"{NS}url" for c in children):
        errors.append("sitemap.xml has non-<url> children of <urlset> (leaked text?)")
    locs = []
    for c in children:
        loc = c.find(f"{NS}loc")
        locs.append(loc.text if loc is not None and loc.text else "")
    if len(locs) != len(set(locs)):
        dups = [l for l in set(locs) if locs.count(l) > 1]
        errors.append(f"sitemap.xml has duplicate <loc> entries: {dups}")

    # Intentionally NOT in the sitemap: theme leftovers (author archive pages are
    # noindexed; tags/categories are empty template dirs) and pagination.
    EXCLUDE_PREFIXES = ("partials/", "author/", "tags/", "categories/", "blog/page/")
    EXCLUDE_FILES = ("404.html",)
    pages = []
    for p in ROOT.rglob("*.html"):
        rel = str(p.relative_to(ROOT))
        if any(rel.startswith(d) for d in EXCLUDE_PREFIXES) or rel in EXCLUDE_FILES:
            continue
        pages.append(rel)
    sm_set = {l.replace("https://cyberalsolutions.com/", "").rstrip("/") for l in locs}
    sm_set = {s if s.endswith(".html") else (s + "/index.html").lstrip("/") for s in sm_set}

    missing = [p for p in pages if p not in sm_set and p != "index.html"]
    if missing:
        errors.append(f"page(s) on disk but missing from sitemap.xml: {missing}")

    for loc in locs:
        rel = loc.replace("https://cyberalsolutions.com/", "")
        t = ROOT / rel
        if not (t.exists() or (t / "index.html").exists() or rel == ""):
            errors.append(f"sitemap.xml lists a URL with no file on disk: {loc}")


def check_no_leaked_line_numbers():
    pat = re.compile(r"^\s*\d+\|", re.M)
    hits = []
    for ext in ("*.html", "*.xml", "*.css", "*.js", "*.txt"):
        for p in ROOT.rglob(ext):
            if pat.search(p.read_text(encoding="utf-8", errors="ignore")):
                hits.append(str(p.relative_to(ROOT)))
    if hits:
        errors.append(
            f"leaked read_file line-number prefixes (NN| at line start) in: {hits}\n"
            "      Fix: strip with a raw-bytes script, never a read_file round-trip."
        )


def check_internal_links():
    broken = []
    for p in ROOT.rglob("*.html"):
        rel = str(p.relative_to(ROOT))
        if rel.startswith(("author/",)):
            continue
        html = p.read_text(encoding="utf-8", errors="ignore")
        for h in set(re.findall(r'href="([^"]+)"', html)):
            if h.startswith(("http", "#", "tel:", "mailto:", "sms:", "//")) or "+" in h or "${" in h:
                continue
            path = h.split("#")[0].split("?")[0]
            if not path:
                continue
            target = (ROOT / path.lstrip("/")) if path.startswith("/") else (p.parent / path)
            if not (target.exists() or (target / "index.html").exists()):
                broken.append(f"{rel} -> {h}")
    if broken:
        errors.append(f"{len(broken)} broken internal link(s):\n      " + "\n      ".join(broken[:15]))


for fn in (check_homepage_matches_blog_index, check_no_orphan_posts, check_sitemap,
           check_no_leaked_line_numbers, check_internal_links):
    try:
        fn()
    except Exception as e:  # a guard that crashes must not look like a pass
        errors.append(f"{fn.__name__} raised {type(e).__name__}: {e}")

if errors:
    print("SEO GUARD FAILED\n")
    for e in errors:
        print(f"  - {e}\n")
    sys.exit(1)

print("SEO guard passed: homepage matches /blog/, no orphaned posts, "
      "sitemap complete and resolvable, no leaked line numbers, no broken internal links.")
