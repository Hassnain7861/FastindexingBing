import streamlit as st
import requests
import xml.etree.ElementTree as ET
import json
import time
from urllib.parse import quote, urlparse

# ──────────────────────────────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IndexNow Fast Indexing Tool",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────
# Custom CSS — Premium Dark Theme
# ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Root overrides */
.stApp {
    background: #0a0e1a;
    font-family: 'Inter', sans-serif;
}

/* Header styling */
.hero-header {
    text-align: center;
    padding: 2rem 0 1.5rem;
}

.hero-header .logo {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 64px;
    height: 64px;
    border-radius: 18px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    box-shadow: 0 8px 32px rgba(99,102,241,0.35);
    font-size: 1.75rem;
    margin-bottom: 0.75rem;
}

.hero-header h1 {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #f1f5f9, #a5b4fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: -0.02em;
}

.hero-header p {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-top: 0.25rem;
}

/* Glass card */
.glass-card {
    background: rgba(17,24,39,0.7);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.25s ease;
}

.glass-card:hover {
    border-color: rgba(99,102,241,0.2);
}

.glass-card h3 {
    color: #f1f5f9;
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.glass-card h3 .step-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    border-radius: 8px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    font-size: 0.75rem;
    font-weight: 700;
    color: #fff;
    flex-shrink: 0;
}

/* Stat boxes */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
    margin: 1rem 0;
}

.stat-box {
    text-align: center;
    padding: 0.75rem 0.5rem;
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.08);
}

.stat-box .value {
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #f1f5f9, #a5b4fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-box .label {
    font-size: 0.7rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.1rem;
}

/* Status badges */
.badge-success {
    display: inline-block;
    padding: 0.15rem 0.55rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    background: rgba(34,197,94,0.15);
    color: #22c55e;
}
.badge-error {
    display: inline-block;
    padding: 0.15rem 0.55rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    background: rgba(239,68,68,0.15);
    color: #ef4444;
}
.badge-warning {
    display: inline-block;
    padding: 0.15rem 0.55rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    background: rgba(245,158,11,0.15);
    color: #f59e0b;
}
.badge-info {
    display: inline-block;
    padding: 0.15rem 0.55rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    background: rgba(59,130,246,0.15);
    color: #3b82f6;
}

/* Curl code block */
.curl-block {
    background: #0d1117;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 1rem;
    font-family: 'Fira Code', 'Cascadia Code', monospace;
    font-size: 0.78rem;
    line-height: 1.7;
    color: #7ee787;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-all;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: #111827 !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}

/* Streamlit widget overrides */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #f1f5f9 !important;
    border-radius: 8px !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.35) !important;
}

div[data-testid="stExpander"] {
    background: rgba(17,24,39,0.7);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
}

/* Button overrides */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    box-shadow: 0 4px 16px rgba(99,102,241,0.35) !important;
    transition: all 0.25s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(99,102,241,0.45) !important;
}

/* Download button */
.stDownloadButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #f1f5f9 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}

.stDownloadButton > button:hover {
    background: rgba(255,255,255,0.08) !important;
    border-color: rgba(255,255,255,0.15) !important;
}

/* Tabs override */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.25rem;
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    padding: 0.25rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    color: #94a3b8;
    font-weight: 600;
    font-size: 0.85rem;
}

.stTabs [aria-selected="true"] {
    background: #6366f1 !important;
    color: #fff !important;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Responsive stat grid */
@media (max-width: 640px) {
    .stat-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
MAX_URLS_PER_BATCH = 10000

STATUS_MESSAGES = {
    200: "OK — Submitted successfully",
    202: "Accepted",
    400: "Bad Request — Invalid format",
    403: "Forbidden — Key not valid",
    422: "Unprocessable — URL/key mismatch",
    429: "Too Many Requests — Slow down",
}

# ──────────────────────────────────────────────────────────────────────
# Session state init
# ──────────────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = []
if "sitemap_urls" not in st.session_state:
    st.session_state.sitemap_urls = []
if "indexnow_key" not in st.session_state:
    st.session_state.indexnow_key = ""
if "indexnow_key_location" not in st.session_state:
    st.session_state.indexnow_key_location = ""

# ──────────────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────────────
def submit_single_url(api_key: str, host: str, url: str, key_location: str = "") -> dict:
    """Submit a single URL via GET request."""
    params = {"url": url, "key": api_key}
    if key_location:
        params["keyLocation"] = key_location
    try:
        resp = requests.get(INDEXNOW_ENDPOINT, params=params, timeout=30)
        msg = STATUS_MESSAGES.get(resp.status_code, f"HTTP {resp.status_code}")
        return {"url": url, "status": resp.status_code, "message": msg}
    except requests.RequestException as e:
        return {"url": url, "status": 0, "message": f"Error: {str(e)}"}


def submit_bulk_urls(api_key: str, host: str, urls: list, key_location: str = "") -> dict:
    """Submit a batch of URLs via POST request."""
    body = {
        "host": host,
        "key": api_key,
        "urlList": urls,
    }
    if key_location:
        body["keyLocation"] = key_location

    try:
        resp = requests.post(
            INDEXNOW_ENDPOINT,
            json=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=60,
        )
        msg = STATUS_MESSAGES.get(resp.status_code, f"HTTP {resp.status_code}")
        return {"status": resp.status_code, "message": msg, "count": len(urls)}
    except requests.RequestException as e:
        return {"status": 0, "message": f"Error: {str(e)}", "count": len(urls)}


# Multiple User-Agents to try when fetching sitemaps (many servers block generic bots)
SITEMAP_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "IndexNow-SitemapFetcher/1.0",
]


def _get_sitemap_response(url: str) -> requests.Response:
    """Try to fetch URL with multiple User-Agents; raise on failure."""
    last_error = None
    for ua in SITEMAP_USER_AGENTS:
        try:
            resp = requests.get(
                url,
                timeout=25,
                headers={
                    "User-Agent": ua,
                    "Accept": "application/xml, text/xml, */*",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                allow_redirects=True,
            )
            if resp.status_code == 200:
                return resp
            if resp.status_code == 403:
                last_error = requests.HTTPError(f"403 Forbidden for url: {url}", response=resp)
                continue
            resp.raise_for_status()
        except requests.RequestException as e:
            last_error = e
            continue
    if last_error is not None:
        raise last_error if isinstance(last_error, requests.RequestException) else requests.RequestException(str(last_error))
    raise requests.RequestException("Failed to fetch sitemap")


def fetch_sitemap(sitemap_url: str) -> list:
    """Fetch and parse a sitemap (or sitemap index), returning a list of URLs."""
    sitemap_url = sitemap_url.strip()
    if not sitemap_url.startswith(("http://", "https://")):
        sitemap_url = "https://" + sitemap_url
    to_fetch = [sitemap_url]
    all_urls = []
    seen = set()
    max_sitemaps = 50  # Limit to avoid runaway

    while to_fetch and len(seen) < max_sitemaps:
        url = to_fetch.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            resp = _get_sitemap_response(url)
        except Exception:
            # If first URL fails, try flipping http <-> https
            if len(seen) == 1 and url == sitemap_url:
                alt = "https://" + url.split("://", 1)[1] if url.startswith("http://") else "http://" + url.split("://", 1)[1]
                try:
                    resp = _get_sitemap_response(alt)
                except Exception as e2:
                    raise e2 from None
            else:
                raise
        root = ET.fromstring(resp.content)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        # Page URLs
        page_urls = [loc.text.strip() for loc in root.findall(".//sm:url/sm:loc", ns) if loc.text]
        if not page_urls:
            page_urls = [loc.text.strip() for loc in root.iter() if loc.tag.endswith("loc") and loc.text]
        # Exclude sitemap URLs from page list (they are indexes)
        page_urls = [u for u in page_urls if "sitemap" not in u.lower().split("/")[-1] or u == url]
        all_urls.extend(page_urls)
        # Child sitemaps (sitemap index)
        child_sitemaps = [loc.text.strip() for loc in root.findall(".//sm:sitemap/sm:loc", ns) if loc.text]
        if not child_sitemaps:
            for el in root.iter():
                if el.tag.endswith("sitemap"):
                    for loc in el.findall(".//{*}loc"):
                        if loc.text:
                            child_sitemaps.append(loc.text.strip())
                            break
        for child in child_sitemaps[:10]:  # Limit child sitemaps per index
            if child not in seen and len(seen) < max_sitemaps:
                to_fetch.append(child)
                seen.add(child)

    return list(dict.fromkeys(all_urls))  # Dedupe, preserve order


def generate_curl_single(api_key: str, url: str, key_location: str = "") -> str:
    params = f"url={quote(url, safe='')}&key={api_key}"
    if key_location:
        params += f"&keyLocation={quote(key_location, safe='')}"
    return f'curl "{INDEXNOW_ENDPOINT}?{params}"'


def generate_curl_bulk(api_key: str, host: str, urls: list, key_location: str = "") -> str:
    body = {"host": host, "key": api_key, "urlList": urls}
    if key_location:
        body["keyLocation"] = key_location
    return (
        f'curl -X POST "{INDEXNOW_ENDPOINT}" \\\n'
        f'  -H "Content-Type: application/json; charset=utf-8" \\\n'
        f"  -d '{json.dumps(body, indent=2)}'"
    )


def status_badge_html(code):
    if code == 200 or code == 202:
        return f'<span class="badge-success">{code} OK</span>'
    elif code == 0:
        return '<span class="badge-warning">ERR</span>'
    elif code >= 400:
        return f'<span class="badge-error">{code}</span>'
    else:
        return f'<span class="badge-info">{code}</span>'


def _host_from_url(url: str) -> str:
    """Derive IndexNow host from a URL (e.g. https://example.com/page -> example.com)."""
    return (urlparse(url).netloc or "").strip() or ""


# ──────────────────────────────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="logo">⚡</div>
    <h1>IndexNow Fast Indexing</h1>
    <p>Paste a URL and submit to Bing & search engines — no forms, just index</p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────
# API key: from secrets (deploy) or session (user set once)
# ──────────────────────────────────────────────────────────────────────
try:
    _secret_key = st.secrets.get("INDEXNOW_KEY", "")
    _secret_location = st.secrets.get("INDEXNOW_KEY_LOCATION", "")
except Exception:
    _secret_key = ""
    _secret_location = ""

# Session overrides secrets (so user can set key once in UI; deployer can set secrets)
api_key = (st.session_state.indexnow_key or _secret_key or "").strip()
key_location = (st.session_state.indexnow_key_location or _secret_location or "").strip()

# Sidebar: only Settings expander (key set once, then hidden)
with st.sidebar:
    with st.expander("⚙️ Settings (API key)", expanded=not bool(api_key)):
        st.caption("Required once. Host is auto-detected from your URL.")
        key_input = st.text_input(
            "IndexNow API key",
            value=st.session_state.indexnow_key,
            placeholder="Paste your key (8–128 hex chars)",
            key="settings_key",
            type="default",
        )
        loc_input = st.text_input(
            "Key file URL (optional)",
            value=st.session_state.indexnow_key_location,
            placeholder="https://yoursite.com/yourkey.txt",
            key="settings_loc",
        )
        if st.button("Save", key="settings_save"):
            st.session_state.indexnow_key = (key_input or "").strip()
            st.session_state.indexnow_key_location = (loc_input or "").strip()
            st.rerun()
        if api_key:
            st.caption(f"✓ Using key …{api_key[-6:] if len(api_key) >= 6 else api_key}")
            if st.download_button(
                label="Download key file",
                data=api_key,
                file_name=f"{api_key}.txt",
                mime="text/plain",
                key="dl_key_sidebar",
            ):
                pass
    st.markdown(
        "<div style='text-align:center;color:#64748b;font-size:0.75rem;'>"
        "Powered by <a href='https://www.indexnow.org' target='_blank' "
        "style='color:#818cf8;text-decoration:none;'>IndexNow.org</a></div>",
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────────────
# Main: Paste URL → Submit (no tabs needed for the main action)
# ──────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="glass-card"><h3><span class="step-badge">⚡</span> Paste URL &amp; Index</h3>'
    "<p style='color:#94a3b8;font-size:0.85rem;margin-bottom:0.75rem;'>"
    "Enter any URL — host is detected automatically. Set your API key once in <strong>Settings</strong> (sidebar) if you haven't.</p></div>",
    unsafe_allow_html=True,
)

single_url = st.text_input(
    "URL",
    placeholder="https://your-site.com/page",
    key="single_url_input",
    label_visibility="collapsed",
)

col_submit, _ = st.columns([1, 3])
with col_submit:
    if st.button("🚀 Index this URL", key="btn_single", use_container_width=True):
        if not api_key:
            st.error("⚠️ Set your API key once in **Settings** (sidebar) to submit.")
        elif not single_url or not single_url.strip().startswith("http"):
            st.error("⚠️ Enter a valid URL to submit.")
        else:
            host = _host_from_url(single_url.strip())
            if not host:
                st.error("⚠️ Could not get host from URL.")
            else:
                with st.spinner("Submitting URL…"):
                    result = submit_single_url(api_key, host, single_url.strip(), key_location)
                    st.session_state.results.insert(0, result)
                if result["status"] in (200, 202):
                    st.success(f"✅ {result['message']}")
                else:
                    st.error(f"❌ {result['message']}")

# ──────────────────────────────────────────────────────────────────────
# Tabs: Bulk, Sitemap, Curl
# ──────────────────────────────────────────────────────────────────────
tab_bulk, tab_sitemap, tab_curl = st.tabs(["📋 Bulk URLs", "🗺️ Sitemap", "💻 Curl Commands"])

# ── Tab: Bulk URLs ────────────────────────────────────────────────────
with tab_bulk:
    st.markdown(
        '<div class="glass-card"><h3><span class="step-badge">2</span> Submit Multiple URLs</h3>'
        "<p style='color:#94a3b8;font-size:0.85rem;margin-bottom:0.75rem;'>"
        "Paste up to 10,000 URLs (one per line) for batch submission.</p></div>",
        unsafe_allow_html=True,
    )

    bulk_text = st.text_area(
        "URLs (one per line)",
        height=200,
        placeholder="https://www.example.com/page-1\nhttps://www.example.com/page-2\nhttps://www.example.com/page-3",
        key="bulk_urls_input",
        label_visibility="collapsed",
    )

    if st.button("🚀 Submit All URLs", key="btn_bulk", use_container_width=True):
        if not api_key:
            st.error("⚠️ Set your API key once in **Settings** (sidebar) to submit.")
        else:
            urls = [u.strip() for u in bulk_text.strip().split("\n") if u.strip().startswith("http")]
            if not urls:
                st.error("⚠️ Add at least one valid URL.")
            elif len(urls) > MAX_URLS_PER_BATCH:
                st.error(f"⚠️ Maximum {MAX_URLS_PER_BATCH} URLs per batch.")
            else:
                host = _host_from_url(urls[0])
                if not host:
                    st.error("⚠️ Could not get host from URLs.")
                else:
                    progress = st.progress(0, text="Submitting URLs…")
                    total = len(urls)
                    success_count = 0
                    fail_count = 0
                    batch_size = min(500, total)
                    batches = [urls[i : i + batch_size] for i in range(0, total, batch_size)]

                    for idx, batch in enumerate(batches):
                        result = submit_bulk_urls(api_key, host, batch, key_location)
                        if result["status"] in (200, 202):
                            success_count += len(batch)
                            for u in batch:
                                st.session_state.results.insert(
                                    0, {"url": u, "status": result["status"], "message": result["message"]}
                                )
                        else:
                            fail_count += len(batch)
                            for u in batch:
                                st.session_state.results.insert(
                                    0, {"url": u, "status": result["status"], "message": result["message"]}
                                )
                        pct = int(((idx + 1) / len(batches)) * 100)
                        progress.progress(pct, text=f"Batch {idx+1}/{len(batches)} — {pct}%")
                        time.sleep(0.1)  # Small delay to avoid 429

                    progress.empty()
                    if success_count:
                        st.success(f"✅ {success_count} URLs submitted successfully!")
                    if fail_count:
                        st.error(f"❌ {fail_count} URLs failed.")

# ── Tab 3: Sitemap ────────────────────────────────────────────────────
with tab_sitemap:
    st.markdown(
        '<div class="glass-card"><h3><span class="step-badge">3</span> Import from Sitemap</h3>'
        "<p style='color:#94a3b8;font-size:0.85rem;margin-bottom:0.75rem;'>"
        "Fetch URLs from your sitemap.xml and submit them all at once.</p></div>",
        unsafe_allow_html=True,
    )

    sitemap_url = st.text_input(
        "Sitemap URL",
        placeholder="https://www.example.com/sitemap.xml",
        key="sitemap_url_input",
        label_visibility="collapsed",
    )
    st.caption("If fetch fails (e.g. 403), open the sitemap in your browser, copy the URLs, and use the **Bulk URLs** tab.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Fetch Sitemap", key="btn_fetch_sitemap", use_container_width=True):
            if not sitemap_url:
                st.error("⚠️ Enter a sitemap URL.")
            else:
                with st.spinner("Fetching sitemap…"):
                    try:
                        fetched = fetch_sitemap(sitemap_url)
                        st.session_state.sitemap_urls = fetched
                        st.success(f"✅ Found {len(fetched)} URLs in sitemap!")
                    except Exception as e:
                        st.session_state.sitemap_urls = []  # Clear stale URLs so UI matches current fetch
                        st.error(f"❌ Failed to fetch sitemap: {e}")
                        st.rerun()

    with col2:
        if st.button(
            f"🚀 Submit {len(st.session_state.sitemap_urls)} URLs",
            key="btn_submit_sitemap",
            use_container_width=True,
            disabled=len(st.session_state.sitemap_urls) == 0,
        ):
            if not api_key:
                st.error("⚠️ Set your API key once in **Settings** (sidebar) to submit.")
            else:
                urls = st.session_state.sitemap_urls
                host = _host_from_url(urls[0]) if urls else ""
                if not host:
                    st.error("⚠️ Could not get host from sitemap URLs.")
                else:
                    progress = st.progress(0, text="Submitting sitemap URLs…")
                    batch_size = min(500, len(urls))
                    batches = [urls[i : i + batch_size] for i in range(0, len(urls), batch_size)]
                    success_count = 0
                    fail_count = 0

                    for idx, batch in enumerate(batches):
                        result = submit_bulk_urls(api_key, host, batch, key_location)
                        if result["status"] in (200, 202):
                            success_count += len(batch)
                            for u in batch:
                                st.session_state.results.insert(
                                    0, {"url": u, "status": result["status"], "message": result["message"]}
                                )
                        else:
                            fail_count += len(batch)
                            for u in batch:
                                st.session_state.results.insert(
                                    0, {"url": u, "status": result["status"], "message": result["message"]}
                                )
                        pct = int(((idx + 1) / len(batches)) * 100)
                        progress.progress(pct, text=f"Batch {idx+1}/{len(batches)} — {pct}%")
                        time.sleep(0.1)

                    progress.empty()
                    if success_count:
                        st.success(f"✅ {success_count} sitemap URLs submitted!")
                    if fail_count:
                        st.error(f"❌ {fail_count} URLs failed.")

    # Show fetched URLs preview
    if st.session_state.sitemap_urls:
        with st.expander(f"Preview URLs ({len(st.session_state.sitemap_urls)} found)", expanded=False):
            st.text("\n".join(st.session_state.sitemap_urls[:100]))
            if len(st.session_state.sitemap_urls) > 100:
                st.caption(f"… and {len(st.session_state.sitemap_urls) - 100} more")

# ── Tab 4: Curl Commands ──────────────────────────────────────────────
with tab_curl:
    st.markdown(
        '<div class="glass-card"><h3><span class="step-badge">💻</span> Curl Commands</h3>'
        "<p style='color:#94a3b8;font-size:0.85rem;margin-bottom:0.75rem;'>"
        "Generate ready-to-use curl commands for your terminal.</p></div>",
        unsafe_allow_html=True,
    )

    curl_url = st.text_input(
        "URL for curl command",
        placeholder="https://www.example.com/page",
        key="curl_url_input",
    )

    curl_bulk_text = st.text_area(
        "Or paste multiple URLs (one per line)",
        height=120,
        key="curl_bulk_input",
    )

    if st.button("⚡ Generate Curl Command", key="btn_gen_curl", use_container_width=True):
        if not api_key:
            st.error("⚠️ Set your API key in **Settings** (sidebar) first.")
        else:
            bulk_urls = [u.strip() for u in curl_bulk_text.strip().split("\n") if u.strip().startswith("http")]
            if bulk_urls:
                host = _host_from_url(bulk_urls[0])
                cmd = generate_curl_bulk(api_key, host, bulk_urls, key_location) if host else None
            elif curl_url and curl_url.strip().startswith("http"):
                cmd = generate_curl_single(api_key, curl_url.strip(), key_location)
            else:
                cmd = None
                st.error("⚠️ Enter at least one URL.")

            if cmd:
                st.markdown(f'<div class="curl-block">{cmd}</div>', unsafe_allow_html=True)
                st.code(cmd, language="bash")

# ──────────────────────────────────────────────────────────────────────
# Results Dashboard
# ──────────────────────────────────────────────────────────────────────
st.markdown("---")

if st.session_state.results:
    total = len(st.session_state.results)
    ok = sum(1 for r in st.session_state.results if r["status"] in (200, 202))
    fail = sum(1 for r in st.session_state.results if r["status"] not in (200, 202, 0))
    errs = sum(1 for r in st.session_state.results if r["status"] == 0)

    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-box"><div class="value">{total}</div><div class="label">Total</div></div>
        <div class="stat-box"><div class="value">{ok}</div><div class="label">Success</div></div>
        <div class="stat-box"><div class="value">{fail}</div><div class="label">Failed</div></div>
        <div class="stat-box"><div class="value">{errs}</div><div class="label">Errors</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Show latest 100 results in a table
    display_results = st.session_state.results[:100]
    table_rows = ""
    for r in display_results:
        badge = status_badge_html(r["status"])
        table_rows += f"<tr><td style='max-width:400px;word-break:break-all;color:#94a3b8;font-size:0.82rem;padding:0.5rem 0.75rem;border-bottom:1px solid rgba(255,255,255,0.08);'>{r['url']}</td><td style='padding:0.5rem 0.75rem;border-bottom:1px solid rgba(255,255,255,0.08);'>{badge}</td><td style='color:#94a3b8;font-size:0.82rem;padding:0.5rem 0.75rem;border-bottom:1px solid rgba(255,255,255,0.08);'>{r['message']}</td></tr>"

    st.markdown(f"""
    <div style="max-height:360px;overflow-y:auto;border-radius:8px;border:1px solid rgba(255,255,255,0.08);">
        <table style="width:100%;border-collapse:collapse;">
            <thead>
                <tr>
                    <th style="position:sticky;top:0;background:#111827;padding:0.65rem 0.75rem;text-align:left;font-weight:600;color:#94a3b8;text-transform:uppercase;font-size:0.7rem;letter-spacing:0.05em;border-bottom:1px solid rgba(255,255,255,0.08);">URL</th>
                    <th style="position:sticky;top:0;background:#111827;padding:0.65rem 0.75rem;text-align:left;font-weight:600;color:#94a3b8;text-transform:uppercase;font-size:0.7rem;letter-spacing:0.05em;border-bottom:1px solid rgba(255,255,255,0.08);">Status</th>
                    <th style="position:sticky;top:0;background:#111827;padding:0.65rem 0.75rem;text-align:left;font-weight:600;color:#94a3b8;text-transform:uppercase;font-size:0.7rem;letter-spacing:0.05em;border-bottom:1px solid rgba(255,255,255,0.08);">Message</th>
                </tr>
            </thead>
            <tbody>{table_rows}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    if len(st.session_state.results) > 100:
        st.caption(f"Showing latest 100 of {len(st.session_state.results)} results.")

    if st.button("🗑️ Clear Results", key="btn_clear"):
        st.session_state.results = []
        st.rerun()
else:
    st.markdown("""
    <div style="text-align:center;padding:2rem;color:#64748b;">
        <div style="font-size:2rem;opacity:0.5;margin-bottom:0.5rem;">📊</div>
        <p style="font-size:0.85rem;">No submissions yet. Submit URLs above to see results here.</p>
    </div>
    """, unsafe_allow_html=True)
