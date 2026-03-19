#!/usr/bin/env python3
"""
HTTP Sitemap Crawler for Odoo Production

Crawls public endpoints to generate a sitemap of accessible routes.

Usage:
    python3 tools/audit/http_crawler.py [base_url] [output_file]

Defaults:
    base_url: https://erp.insightpulseai.com
    output_file: docs/runtime/HTTP_SITEMAP.prod.json
"""

import json
import re
import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse
from collections import deque

# Try to import requests, fall back to urllib
try:
    import requests
    USE_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    import ssl
    USE_REQUESTS = False


def fetch_url(url, timeout=10):
    """Fetch URL and return (status_code, content_type, content)."""
    try:
        if USE_REQUESTS:
            resp = requests.get(url, timeout=timeout, allow_redirects=True, verify=True)
            return resp.status_code, resp.headers.get('Content-Type', ''), resp.text
        else:
            ctx = ssl.create_default_context()
            req = urllib.request.Request(url, headers={'User-Agent': 'OdooSitemapCrawler/1.0'})
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                content = resp.read().decode('utf-8', errors='replace')
                return resp.status, resp.headers.get('Content-Type', ''), content
    except Exception as e:
        return 0, 'error', str(e)


def extract_links(html, base_url):
    """Extract internal links from HTML."""
    links = set()

    # href patterns
    for match in re.finditer(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE):
        href = match.group(1)
        if not href.startswith(('javascript:', 'mailto:', 'tel:', '#', 'data:')):
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                links.add(full_url)

    # action patterns (forms)
    for match in re.finditer(r'action=["\']([^"\']+)["\']', html, re.IGNORECASE):
        action = match.group(1)
        if not action.startswith(('javascript:', 'mailto:')):
            full_url = urljoin(base_url, action)
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                links.add(full_url)

    return links


def crawl(base_url, max_depth=3, max_pages=100):
    """BFS crawl from base_url up to max_depth."""
    visited = {}
    queue = deque([(base_url, 0)])

    # Seed URLs
    seed_urls = [
        '/web',
        '/web/login',
        '/web/database/selector',
        '/web/webclient/version_info',
    ]

    for path in seed_urls:
        url = urljoin(base_url, path)
        if url not in [u for u, _ in queue]:
            queue.append((url, 0))

    while queue and len(visited) < max_pages:
        url, depth = queue.popleft()

        # Normalize URL (remove query params for dedup)
        normalized = urlparse(url)._replace(query='', fragment='').geturl()

        if normalized in visited:
            continue

        print(f"  [{len(visited)+1}/{max_pages}] {url[:80]}...")
        status, content_type, content = fetch_url(url)

        visited[normalized] = {
            'url': url,
            'status': status,
            'content_type': content_type.split(';')[0] if content_type else '',
            'depth': depth,
        }

        # Extract links if HTML and not at max depth
        if depth < max_depth and 'html' in content_type.lower() and status in (200, 303):
            for link in extract_links(content, url):
                link_normalized = urlparse(link)._replace(query='', fragment='').geturl()
                if link_normalized not in visited:
                    queue.append((link, depth + 1))

    return visited


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'https://erp.insightpulseai.com'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'docs/runtime/HTTP_SITEMAP.prod.json'

    print(f"=== HTTP Sitemap Crawler ===")
    print(f"Base URL: {base_url}")
    print(f"Output: {output_file}")
    print("")

    print("Crawling (max depth=3, max pages=100)...")
    pages = crawl(base_url)

    # Build report
    report = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'base_url': base_url,
        'pages_crawled': len(pages),
        'pages': list(pages.values()),
        'status_summary': {},
    }

    # Status summary
    for page in pages.values():
        status = page['status']
        report['status_summary'][status] = report['status_summary'].get(status, 0) + 1

    # Sort pages by URL
    report['pages'].sort(key=lambda p: p['url'])

    # Write output
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print("")
    print(f"=== Crawl Complete ===")
    print(f"Pages crawled: {len(pages)}")
    print(f"Status summary: {report['status_summary']}")
    print(f"Output: {output_file}")


if __name__ == '__main__':
    main()
