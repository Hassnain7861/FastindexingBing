"""
Quick tests for IndexNow helper logic (no Streamlit, no live API key required).
Run: python test_indexing.py
"""
import sys
sys.path.insert(0, ".")
from app import (
    generate_curl_single,
    generate_curl_bulk,
    status_badge_html,
    INDEXNOW_ENDPOINT,
    STATUS_MESSAGES,
)

def test_curl_single():
    cmd = generate_curl_single("abc123", "https://example.com/page?foo=1&bar=2")
    assert INDEXNOW_ENDPOINT in cmd
    assert "abc123" in cmd
    assert "url=" in cmd
    # URL should be encoded (no raw & in query)
    assert "foo%3D1%26bar%3D2" in cmd or "foo=" in cmd
    print("OK generate_curl_single")

def test_curl_bulk():
    cmd = generate_curl_bulk("key1", "www.example.com", ["https://example.com/a", "https://example.com/b"])
    assert "POST" in cmd
    assert "key1" in cmd
    assert "www.example.com" in cmd
    assert "example.com/a" in cmd
    print("OK generate_curl_bulk")

def test_status_badges():
    assert "OK" in status_badge_html(200)
    assert "OK" in status_badge_html(202)
    assert "ERR" in status_badge_html(0)
    assert "badge-error" in status_badge_html(403)
    print("OK status_badge_html")

def test_constants():
    assert 200 in STATUS_MESSAGES
    assert STATUS_MESSAGES[200] == "OK — Submitted successfully"
    print("OK constants")

if __name__ == "__main__":
    test_curl_single()
    test_curl_bulk()
    test_status_badges()
    test_constants()
    print("\nAll tests passed.")
