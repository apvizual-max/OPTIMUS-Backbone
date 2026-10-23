import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../20_BRIDGES/minimax/shared")))

from minimax_bridge_core import check_health_endpoint

def test_check_health_endpoint_ssrf():
    # Pass empty title to verify default fallback title behavior
    check_fn = check_health_endpoint("file:///etc/passwd", "svc.test", "")
    check = check_fn()
    assert check.severity == "fail"
    assert "Invalid URL scheme" in check.title
    assert "Security: URL scheme must be http or https" in check.detail
    assert check.evidence.get("scheme") == "file"

def test_check_health_endpoint_valid_scheme():
    # just testing that it doesn't fail with "Invalid URL scheme" for valid scheme
    # it will probably fail with unreachable, which is fine
    check_fn = check_health_endpoint("http://localhost:12345/health", "svc.test", "Test valid")
    check = check_fn()
    assert check.title != "Invalid URL scheme"
    if check.severity == "fail":
        assert "unreachable" in check.title or "unreachable" in check.detail or "ConnectionRefusedError" in check.detail or "URLError" in check.detail
