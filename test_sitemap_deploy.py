"""
Deploy test: fetch the 3 sitemaps and verify IndexNow submission with API key.
Usage: python test_sitemap_deploy.py <API_KEY>
Or: set INDEXNOW_KEY=yourkey && python test_sitemap_deploy.py
"""
import os
import sys
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"

SITEMAP_URLS = [
    "https://emergencyplumberportland.org/sitemap.xml",
    "https://www.localserpchecker.app/sitemap.xml",
    "http://autoelectrician.org/sitemap.xml",
]

SITEMAP_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
]


def get_sitemap_response(url: str) -> requests.Response:
    for ua in SITEMAP_USER_AGENTS:
        try:
            r = requests.get(
                url, timeout=25,
                headers={"User-Agent": ua, "Accept": "application/xml, text/xml, */*", "Accept-Language": "en-US,en;q=0.9"},
                allow_redirects=True,
            )
            if r.status_code == 200:
                return r
            if r.status_code == 403:
                continue
            r.raise_for_status()
        except requests.RequestException:
            continue
    raise requests.RequestException(f"Failed to fetch sitemap: {url}")


def fetch_sitemap(sitemap_url: str) -> list:
    sitemap_url = sitemap_url.strip()
    if not sitemap_url.startswith(("http://", "https://")):
        sitemap_url = "https://" + sitemap_url
    to_fetch = [sitemap_url]
    all_urls = []
    seen = set()
    max_sitemaps = 50

    while to_fetch and len(seen) < max_sitemaps:
        url = to_fetch.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            resp = get_sitemap_response(url)
        except Exception:
            if len(seen) == 1 and url == sitemap_url:
                alt = "https://" + url.split("://", 1)[1] if url.startswith("http://") else "http://" + url.split("://", 1)[1]
                try:
                    resp = get_sitemap_response(alt)
                except Exception as e2:
                    raise e2 from None
            else:
                raise
        root = ET.fromstring(resp.content)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        page_urls = [loc.text.strip() for loc in root.findall(".//sm:url/sm:loc", ns) if loc.text]
        if not page_urls:
            page_urls = [loc.text.strip() for loc in root.iter() if loc.tag.endswith("loc") and loc.text]
        page_urls = [u for u in page_urls if "sitemap" not in u.lower().split("/")[-1] or u == url]
        all_urls.extend(page_urls)
        child_sitemaps = [loc.text.strip() for loc in root.findall(".//sm:sitemap/sm:loc", ns) if loc.text]
        if not child_sitemaps:
            for el in root.iter():
                if el.tag.endswith("sitemap"):
                    for loc in el.findall(".//{*}loc"):
                        if loc.text:
                            child_sitemaps.append(loc.text.strip())
                            break
        for child in child_sitemaps[:10]:
            if child not in seen and len(seen) < max_sitemaps:
                to_fetch.append(child)
                seen.add(child)

    return list(dict.fromkeys(all_urls))


def submit_single_url(api_key: str, host: str, url: str) -> dict:
    try:
        r = requests.get(INDEXNOW_ENDPOINT, params={"url": url, "key": api_key}, timeout=30)
        return {"status": r.status_code, "message": r.status_code}
    except requests.RequestException as e:
        return {"status": 0, "message": str(e)}


def main():
    api_key = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("INDEXNOW_KEY") or "").strip()
    if not api_key:
        print("Usage: python test_sitemap_deploy.py <API_KEY>")
        sys.exit(1)

    print("=" * 60)
    print("SITEMAP FETCH TEST")
    print("=" * 60)

    results = []
    for url in SITEMAP_URLS:
        try:
            urls = fetch_sitemap(url)
            results.append((url, len(urls), urls, None))
            print(f"  OK   {url}  ->  {len(urls)} URLs")
        except Exception as e:
            results.append((url, 0, [], str(e)))
            print(f"  FAIL {url}")
            print(f"       {e}")

    print()
    print("INDEXNOW SUBMISSION TEST (1 URL per successful sitemap)")
    print("=" * 60)

    for url, count, urls, err in results:
        if err or not urls:
            continue
        first_url = urls[0]
        parsed = urlparse(first_url)
        host = parsed.netloc or ""
        r = submit_single_url(api_key, host, first_url)
        status = r["status"]
        if status in (200, 202):
            print(f"  OK   {host}  -> {status} Accepted")
        else:
            print(f"  --   {host}  -> {status} (check key/host match)")

    print()
    failed = [r[0] for r in results if r[3] is not None]
    if failed:
        print("Note: Sitemap fetch failed for:", ", ".join(failed))
    else:
        print("All 3 sitemaps fetched successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()
