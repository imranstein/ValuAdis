"""Global error handling tests."""

from fastapi.testclient import TestClient

from app.main import app


def _qa_error_route():
    raise RuntimeError("qa failure")


app.add_api_route(
    "/api/v1/_qa_unhandled_exception",
    _qa_error_route,
    methods=["GET"],
    include_in_schema=False,
)


def test_unhandled_exceptions_return_json_payload():
    qa_client = TestClient(app, raise_server_exceptions=False)
    response = qa_client.get("/api/v1/_qa_unhandled_exception")

    assert response.status_code == 500
    payload = response.json()
    assert payload == {"success": False, "message": "Internal server error"}
