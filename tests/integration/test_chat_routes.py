
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_query_manager
from app.main import app


class FakeConversationRepository:
    def get_by_id(self, conversation_id):
        return None


class FakeQueryManager:
    def __init__(self, *, fail_execute=False, fail_stream=False):
        self.fail_execute = fail_execute
        self.fail_stream = fail_stream
        self.conversation_repository = FakeConversationRepository()

    def execute(self, **kwargs):
        if self.fail_execute:
            raise RuntimeError("Sensitive internal database detail")

        return SimpleNamespace(
            conversation_id="test-conversation-id",
            response="Hello from MRBot",
        )

    def execute_stream(self, **kwargs):
        if self.fail_stream:
            raise RuntimeError("Sensitive internal stream detail")

        yield "Hello"
        yield " from MRBot"


@pytest.fixture
def client():
    def override_query_manager():
        return FakeQueryManager()

    app.dependency_overrides[get_query_manager] = override_query_manager

    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_query_manager, None)


def test_invalid_chat_request_returns_structured_422(client):
    response = client.post("/api/v1/chat", json={})

    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "validation_error"
    assert body["message"] == (
        "The request contains invalid or missing fields."
    )


def test_unexpected_chat_error_returns_safe_500():
    app.dependency_overrides[get_query_manager] = lambda: FakeQueryManager(
        fail_execute=True
    )

    try:
        with TestClient(
            app, raise_server_exceptions=False
        ) as test_client:
            response = test_client.post(
                "/api/v1/chat",
                json={"message": "Hello"},
            )

        assert response.status_code == 500
        body = response.json()
        assert body["error"] == "internal_server_error"
        assert "Sensitive internal database detail" not in response.text
    finally:
        app.dependency_overrides.pop(get_query_manager, None)


def test_stream_failure_returns_safe_sse_error():
    app.dependency_overrides[get_query_manager] = lambda: FakeQueryManager(
        fail_stream=True
    )

    try:
        with TestClient(
            app, raise_server_exceptions=False
        ) as test_client:
            response = test_client.post(
                "/api/v1/chat/stream",
                json={"message": "Hello"},
            )

        assert response.status_code == 200
-        assert response.headers["content-type"].startswith(
            "text/event-stream"
        )
        assert "event: error" in response.text
        assert '"error": "stream_generation_failed"' in response.text
        assert "Unable to generate a response." in response.text
        assert "Sensitive internal stream detail" not in response.text
    finally:
        app.dependency_overrides.pop(get_query_manager, None)


def test_successful_stream_ends_with_done_event(client):
    response = client.post(
        "/api/v1/chat/stream",
        json={"message": "Hello"},
    )

    assert response.status_code == 200
    assert "event: token" in response.text
    assert "Hello" in response.text
    assert "event: done" in response.text
