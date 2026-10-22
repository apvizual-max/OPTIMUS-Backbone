🎯 **What:** The `check_health_endpoint` function in `minimax_bridge_core.py` was vulnerable to Server-Side Request Forgery (SSRF). Specifically, `urllib.request.urlopen` processes URL schemas blindly.
⚠️ **Risk:** A malicious or improperly sanitized URL could exploit schemas like `file://` to perform local file reads (e.g., `file:///etc/passwd`).
🛡️ **Solution:** Added URL scheme validation using `urllib.parse.urlparse` to ensure the URL utilizes only `http` or `https` prior to execution. Invalid schemas now return an immediate failed `Check` object.
