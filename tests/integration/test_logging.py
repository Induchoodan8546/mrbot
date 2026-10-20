
import logging
import re

from fastapi.testclient import TestClient

from app.main import app


def test_successful_request_is_logged(caplog):
    with caplog.at_level(logging.INFO, logger="app.main"):
        with TestClient(app) as client:
            response = client.get("/")

    assert response.status_code == 200

    assert re.search(
        r"HTTP GET / \| status=200 \| duration_ms=\d+\.\d+",
        caplog.text,
    )


def test_validation_error_is_logged(caplog):
    with caplog.at_level(
        logging.WARNING,
        logger="app.core.exception_handlers",
    ):
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/chat",
                json={},
            )

    assert response.status_code == 422
    assert "Request validation failed: POST /api/v1/chat" in caplog.text


def test_request_log_does_not_contain_message_body(caplog):
    private_message = "PRIVATE_TEST_MESSAGE_12345"

    with caplog.at_level(logging.INFO, logger="app.main"):
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/chat",
                json={"message": private_message, "temperature": 5.0},
            )

    assert response.status_code == 422
    assert private_message not in caplog.text
