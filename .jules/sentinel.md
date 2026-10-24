## 2024-05-24 - Unrestricted urllib Request (SSRF)
**Vulnerability:** `check_health_endpoint` in `minimax_bridge_core.py` used `urllib.request.urlopen(url)` without validating the URL scheme, allowing local file read via `file://` (e.g. `file:///etc/passwd`).
**Learning:** Python's `urllib` natively supports `file://` schemas, which can lead to SSRF or local file inclusion if arbitrary URLs are passed into health check endpoints.
**Prevention:** Always parse URLs with `urllib.parse.urlparse` and validate that the scheme is explicitly allowed (e.g. `http` or `https`) before calling `urlopen`.
