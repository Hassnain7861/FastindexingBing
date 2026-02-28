# IndexNow Fast Indexing Tool

Submit URLs to **Bing** and other search engines instantly via the [IndexNow](https://www.indexnow.org) protocol. Built with Streamlit.

## Features

- **Single URL** — Submit one URL at a time
- **Bulk URLs** — Paste up to 10,000 URLs (one per line)
- **Sitemap** — Fetch URLs from a sitemap and submit in one go
- **Curl commands** — Generate ready-to-use curl commands

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

## Deploy on Streamlit Community Cloud

1. **Push this app to GitHub**  
   Create a repo and push this folder (include `app.py`, `requirements.txt`, and `.streamlit/config.toml`).

2. **Deploy**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click **“New app”**
   - Choose your repo, branch (e.g. `main`), and set **Main file path** to `app.py`
   - Click **“Deploy”**

3. **Optional — Advanced settings**
   - **Python version**: 3.10 or 3.12 (default is fine)
   - No secrets required; users enter their IndexNow API key in the app sidebar

Your app will get a URL like `https://your-app-name.streamlit.app`.

## IndexNow setup

1. Create an API key (8–128 hex characters) or use an existing one.
2. Put the key file (e.g. `yourkey.txt` containing the key) on your website, e.g. `https://yoursite.com/yourkey.txt`.
3. In the app sidebar, enter **API Key**, **Website Host** (e.g. `www.yoursite.com`), and optionally **Key File Location** if it’s not at the root.

## Requirements

- Python 3.10+
- `streamlit>=1.30.0`
- `requests>=2.31.0`
