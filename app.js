/* ===================================================================
   IndexNow Fast Indexing Tool — app.js
   Handles: URL submission (single + bulk), sitemap parsing,
            key-file generation, curl command generation, live status log
   =================================================================== */

(function () {
    'use strict';

    // ── Config ──────────────────────────────────────────────────────────
    const INDEXNOW_ENDPOINT = 'https://api.indexnow.org/indexnow';
    const MAX_URLS_PER_BATCH = 10000;
    const CORS_PROXY = ''; // Leave empty; we'll generate curl commands as fallback

    // ── DOM refs ────────────────────────────────────────────────────────
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    // Form fields
    const apiKeyInput = $('#apiKey');
    const hostInput = $('#host');
    const keyLocationInput = $('#keyLocation');

    // Tabs
    const tabs = $$('.tab');
    const tabContents = $$('.tab-content');

    // Single URL
    const singleUrlInput = $('#singleUrl');
    const btnSubmitSingle = $('#btnSubmitSingle');

    // Bulk URLs
    const bulkUrlsTextarea = $('#bulkUrls');
    const btnSubmitBulk = $('#btnSubmitBulk');

    // Sitemap
    const sitemapUrlInput = $('#sitemapUrl');
    const btnFetchSitemap = $('#btnFetchSitemap');
    const btnSubmitSitemap = $('#btnSubmitSitemap');
    const sitemapStatus = $('#sitemapStatus');

    // Key file
    const btnDownloadKey = $('#btnDownloadKey');
    const keyPreviewEl = $('#keyPreview');

    // Results
    const progressBar = $('#progressBar');
    const statTotal = $('#statTotal');
    const statSuccess = $('#statSuccess');
    const statFailed = $('#statFailed');
    const statPending = $('#statPending');
    const logBody = $('#logBody');
    const emptyState = $('#emptyState');

    // Curl
    const curlOutput = $('#curlOutput');
    const btnCopyCurl = $('#btnCopyCurl');

    // Toast container
    const toastContainer = $('#toastContainer');

    // ── State ───────────────────────────────────────────────────────────
    let sitemapUrls = [];
    let stats = { total: 0, success: 0, failed: 0, pending: 0 };

    // ── Tabs ────────────────────────────────────────────────────────────
    tabs.forEach((tab) => {
        tab.addEventListener('click', () => {
            tabs.forEach((t) => t.classList.remove('active'));
            tabContents.forEach((c) => c.classList.remove('active'));
            tab.classList.add('active');
            const target = tab.dataset.tab;
            $(`#tab-${target}`).classList.add('active');
        });
    });

    // ── Toasts ──────────────────────────────────────────────────────────
    function toast(message, type = 'info') {
        const el = document.createElement('div');
        el.className = `toast toast-${type}`;
        el.textContent = message;
        toastContainer.appendChild(el);
        setTimeout(() => el.remove(), 4000);
    }

    // ── Validation ──────────────────────────────────────────────────────
    function getConfig() {
        const key = apiKeyInput.value.trim();
        const host = hostInput.value.trim().replace(/^https?:\/\//, '').replace(/\/+$/, '');
        const keyLocation = keyLocationInput.value.trim();

        if (!key) { toast('Please enter your API key.', 'error'); return null; }
        if (!host) { toast('Please enter your website host.', 'error'); return null; }
        return { key, host, keyLocation };
    }

    function parseUrls(text) {
        return text
            .split(/[\n,]+/)
            .map((u) => u.trim())
            .filter((u) => u && (u.startsWith('http://') || u.startsWith('https://')));
    }

    // ── Stats helpers ───────────────────────────────────────────────────
    function resetStats(total) {
        stats = { total, success: 0, failed: 0, pending: total };
        updateStatsUI();
        progressBar.style.width = '0%';
        logBody.innerHTML = '';
        emptyState.style.display = 'none';
    }

    function updateStatsUI() {
        statTotal.textContent = stats.total;
        statSuccess.textContent = stats.success;
        statFailed.textContent = stats.failed;
        statPending.textContent = stats.pending;
        const pct = stats.total ? Math.round(((stats.success + stats.failed) / stats.total) * 100) : 0;
        progressBar.style.width = pct + '%';
    }

    function addLogEntry(url, status, message) {
        const tr = document.createElement('tr');
        let badgeClass = 'pending';
        if (status >= 200 && status < 300) badgeClass = 'success';
        else if (status >= 400) badgeClass = 'error';

        tr.innerHTML = `
      <td style="max-width:400px">${escapeHtml(url)}</td>
      <td><span class="status-badge ${badgeClass}">${status}</span></td>
      <td>${escapeHtml(message)}</td>
    `;
        logBody.prepend(tr);
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // ── Status code meaning ─────────────────────────────────────────────
    function statusMessage(code) {
        const map = {
            200: 'OK — Submitted',
            202: 'Accepted',
            400: 'Bad Request',
            403: 'Forbidden — Key invalid',
            422: 'Unprocessable — URL/key mismatch',
            429: 'Too Many Requests',
        };
        return map[code] || `HTTP ${code}`;
    }

    // ── Submit Single URL ──────────────────────────────────────────────
    btnSubmitSingle.addEventListener('click', async () => {
        const config = getConfig();
        if (!config) return;

        const url = singleUrlInput.value.trim();
        if (!url) { toast('Enter a URL to submit.', 'error'); return; }

        resetStats(1);
        btnSubmitSingle.disabled = true;
        btnSubmitSingle.innerHTML = '<span class="spinner"></span> Submitting…';

        try {
            const endpoint = `${INDEXNOW_ENDPOINT}?url=${encodeURIComponent(url)}&key=${config.key}`;
            const res = await fetch(endpoint, { method: 'GET', mode: 'cors' });
            stats.pending--;
            if (res.ok) { stats.success++; } else { stats.failed++; }
            addLogEntry(url, res.status, statusMessage(res.status));
        } catch (err) {
            stats.pending--;
            stats.failed++;
            addLogEntry(url, 'CORS', 'Blocked by CORS — use the curl command below');
            generateCurlSingle(config, url);
        }

        updateStatsUI();
        btnSubmitSingle.disabled = false;
        btnSubmitSingle.innerHTML = '🚀 Submit URL';
        toast(stats.success ? 'URL submitted!' : 'Submission failed — check curl tab.', stats.success ? 'success' : 'error');
    });

    // ── Submit Bulk URLs ───────────────────────────────────────────────
    btnSubmitBulk.addEventListener('click', async () => {
        const config = getConfig();
        if (!config) return;

        const urls = parseUrls(bulkUrlsTextarea.value);
        if (!urls.length) { toast('Add at least one valid URL.', 'error'); return; }
        if (urls.length > MAX_URLS_PER_BATCH) {
            toast(`Max ${MAX_URLS_PER_BATCH} URLs per batch.`, 'error');
            return;
        }

        await submitBulk(config, urls, btnSubmitBulk);
    });

    async function submitBulk(config, urls, btn) {
        resetStats(urls.length);
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Submitting…';

        const body = {
            host: config.host,
            key: config.key,
            urlList: urls,
        };
        if (config.keyLocation) body.keyLocation = config.keyLocation;

        try {
            const res = await fetch(INDEXNOW_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json; charset=utf-8' },
                body: JSON.stringify(body),
                mode: 'cors',
            });

            urls.forEach((url) => {
                stats.pending--;
                if (res.ok) { stats.success++; } else { stats.failed++; }
                addLogEntry(url, res.status, statusMessage(res.status));
            });
        } catch (err) {
            urls.forEach((url) => {
                stats.pending--;
                stats.failed++;
                addLogEntry(url, 'CORS', 'Blocked — use curl command below');
            });
            generateCurlBulk(config, urls);
        }

        updateStatsUI();
        btn.disabled = false;
        btn.innerHTML = '🚀 Submit All URLs';
        toast(stats.success ? `${stats.success} URLs submitted!` : 'Submission failed — check curl tab.', stats.success ? 'success' : 'error');
    }

    // ── Sitemap Fetch ──────────────────────────────────────────────────
    btnFetchSitemap.addEventListener('click', async () => {
        const url = sitemapUrlInput.value.trim();
        if (!url) { toast('Enter a sitemap URL.', 'error'); return; }

        btnFetchSitemap.disabled = true;
        btnFetchSitemap.innerHTML = '<span class="spinner"></span> Fetching…';
        sitemapStatus.textContent = 'Fetching sitemap…';

        try {
            // Try direct fetch first
            let text;
            try {
                const res = await fetch(url, { mode: 'cors' });
                text = await res.text();
            } catch {
                // Use allorigins proxy as fallback
                const proxyUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`;
                const res = await fetch(proxyUrl);
                text = await res.text();
            }

            const parser = new DOMParser();
            const xml = parser.parseFromString(text, 'text/xml');
            const locs = xml.querySelectorAll('loc');
            sitemapUrls = Array.from(locs).map((el) => el.textContent.trim());

            if (sitemapUrls.length === 0) {
                sitemapStatus.textContent = 'No <loc> entries found in sitemap.';
                toast('No URLs found in sitemap.', 'error');
            } else {
                sitemapStatus.textContent = `✅ Found ${sitemapUrls.length} URLs`;
                btnSubmitSitemap.style.display = 'inline-flex';
                toast(`${sitemapUrls.length} URLs extracted from sitemap.`, 'success');
            }
        } catch (err) {
            sitemapStatus.textContent = 'Failed to fetch sitemap. Try downloading it and pasting URLs in the Bulk tab.';
            toast('Could not fetch sitemap.', 'error');
        }

        btnFetchSitemap.disabled = false;
        btnFetchSitemap.innerHTML = '📥 Fetch Sitemap';
    });

    btnSubmitSitemap.addEventListener('click', async () => {
        if (!sitemapUrls.length) { toast('Fetch a sitemap first.', 'error'); return; }
        const config = getConfig();
        if (!config) return;
        await submitBulk(config, sitemapUrls, btnSubmitSitemap);
    });

    // ── Key File Download ─────────────────────────────────────────────
    apiKeyInput.addEventListener('input', updateKeyPreview);
    function updateKeyPreview() {
        const key = apiKeyInput.value.trim();
        if (key) {
            keyPreviewEl.innerHTML = `<span class="filename">📄 ${key}.txt</span>`;
        } else {
            keyPreviewEl.innerHTML = '<span class="filename">Enter your API key above</span>';
        }
    }

    btnDownloadKey.addEventListener('click', () => {
        const key = apiKeyInput.value.trim();
        if (!key) { toast('Enter your API key first.', 'error'); return; }

        const blob = new Blob([key], { type: 'text/plain;charset=utf-8' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `${key}.txt`;
        a.click();
        URL.revokeObjectURL(a.href);
        toast(`Downloaded ${key}.txt — upload it to your website root.`, 'success');
    });

    // ── Curl Command Generation ────────────────────────────────────────
    function generateCurlSingle(config, url) {
        let cmd = `curl "${INDEXNOW_ENDPOINT}?url=${encodeURIComponent(url)}&key=${config.key}`;
        if (config.keyLocation) cmd += `&keyLocation=${encodeURIComponent(config.keyLocation)}`;
        cmd += '"';
        curlOutput.textContent = cmd;
    }

    function generateCurlBulk(config, urls) {
        const body = {
            host: config.host,
            key: config.key,
            urlList: urls,
        };
        if (config.keyLocation) body.keyLocation = config.keyLocation;

        const cmd = `curl -X POST "${INDEXNOW_ENDPOINT}" \\
  -H "Content-Type: application/json; charset=utf-8" \\
  -d '${JSON.stringify(body, null, 2)}'`;
        curlOutput.textContent = cmd;
    }

    btnCopyCurl.addEventListener('click', () => {
        const text = curlOutput.textContent;
        if (!text || text === 'Curl commands will appear here when needed…') {
            toast('No curl command to copy.', 'info');
            return;
        }
        navigator.clipboard.writeText(text).then(() => {
            toast('Copied to clipboard!', 'success');
        });
    });

    // ── Generate Curl (manual button) ──────────────────────────────────
    $('#btnGenerateCurl').addEventListener('click', () => {
        const config = getConfig();
        if (!config) return;

        // Try to gather URLs from whichever tab is active
        const activeTab = document.querySelector('.tab.active').dataset.tab;
        let urls = [];

        if (activeTab === 'single') {
            const u = singleUrlInput.value.trim();
            if (u) urls = [u];
        } else if (activeTab === 'bulk') {
            urls = parseUrls(bulkUrlsTextarea.value);
        } else if (activeTab === 'sitemap') {
            urls = sitemapUrls;
        }

        if (!urls.length) {
            toast('Add some URLs first.', 'error');
            return;
        }

        if (urls.length === 1) {
            generateCurlSingle(config, urls[0]);
        } else {
            generateCurlBulk(config, urls);
        }
        toast('Curl command generated!', 'success');
    });

    // ── Init ────────────────────────────────────────────────────────────
    updateKeyPreview();

})();
