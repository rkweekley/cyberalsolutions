#!/usr/bin/env python3
"""Simple site link checker for local static server.

Usage: python tools/link_checker.py
"""
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen, Request
import sys


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and 'href' in attrs:
            self.links.add(attrs['href'])
        elif tag in ('img', 'script') and 'src' in attrs:
            self.links.add(attrs['src'])
        elif tag == 'link' and 'href' in attrs:
            self.links.add(attrs['href'])


def is_skippable(link):
    if not link:
        return True
    link = link.strip()
    if link.startswith('#'):
        return True
    scheme = urlparse(link).scheme
    if scheme in ('mailto', 'tel', 'javascript'):
        return True
    return False


def check_url(url, timeout=10):
    try:
        req = Request(url, headers={'User-Agent': 'LinkChecker/1.0'})
        with urlopen(req, timeout=timeout) as resp:
            return resp.getcode()
    except Exception as e:
        return str(e)


def crawl(base):
    to_visit = [base]
    visited = set()
    broken = []
    checked = set()

    while to_visit:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)
        print('Crawling', url)
        code = check_url(url)
        checked.add((url, code))
        if isinstance(code, int) and 200 <= code < 400:
            # parse links
            try:
                req = Request(url, headers={'User-Agent': 'LinkChecker/1.0'})
                with urlopen(req, timeout=10) as resp:
                    content_type = resp.headers.get('Content-Type', '')
                    if 'text/html' in content_type:
                        data = resp.read().decode('utf-8', errors='ignore')
                        p = LinkParser()
                        p.feed(data)
                        for raw in p.links:
                            if is_skippable(raw):
                                continue
                            joined = urljoin(url, raw)
                            parsed = urlparse(joined)
                            base_parsed = urlparse(base)
                            # only follow same-host links
                            if parsed.scheme in ('http', 'https') and parsed.netloc == base_parsed.netloc:
                                if joined not in visited and joined not in to_visit:
                                    to_visit.append(joined)
                            # check asset links too
                            if joined not in checked:
                                code2 = check_url(joined)
                                if not (isinstance(code2, int) and 200 <= code2 < 400):
                                    broken.append((joined, code2))
            except Exception as e:
                broken.append((url, str(e)))
        else:
            broken.append((url, code))

    return checked, broken


def main():
    base = 'http://127.0.0.1:8000/'
    print('Starting link crawl at', base)
    checked, broken = crawl(base)
    print('\nChecked {} resources.'.format(len(checked)))
    if not broken:
        print('No broken links found.')
        sys.exit(0)
    else:
        print('Broken links:')
        for url, err in broken:
            print('-', url, '->', err)
        sys.exit(2)


if __name__ == '__main__':
    main()
