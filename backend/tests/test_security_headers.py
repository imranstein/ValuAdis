"""
Security Header Tests

Validate that API responses include critical security headers.
"""


def test_security_headers_are_present_on_health(client):
    response = client.get("/health")
    assert response.status_code == 200

    headers = response.headers
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "DENY"
    assert headers["x-xss-protection"] == "1; mode=block"
    assert headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert headers["permissions-policy"] == "geolocation=(), microphone=()"
    assert headers["cross-origin-resource-policy"] == "same-origin"
    assert headers["cross-origin-opener-policy"] == "same-origin"
    assert (
        headers["content-security-policy"]
        == "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'; connect-src 'self'"
    )


def test_security_headers_apply_to_error_routes(client):
    response = client.get("/this-endpoint-does-not-exist")
    assert response.status_code == 404

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
