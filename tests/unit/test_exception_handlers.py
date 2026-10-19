
import json
import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError

from app.core.exception_handlers import (
    unexpected_exception_handler,
    validation_exception_handler,
)


def make_request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/chat",
            "headers": [],
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("testclient", 123),
        }
    )


def test_validation_handler_returns_structured_422():
    request = make_request()

    exc = RequestValidationError(
        [
            {
                "type": "missing",
                "loc": ("body", "message"),
                "msg": "Field required",
                "input": {},
            }
        ]
    )

    response = __import__("asyncio").run(
        validation_exception_handler(request, exc)
    )

    body = json.loads(response.body)

    assert response.status_code == 422
    assert body["error"] == "validation_error"
    assert body["message"] == (
        "The request contains invalid or missing fields."
    )
    assert body["details"][0]["loc"] == ["body", "message"]


def test_unexpected_exception_handler_returns_safe_500(caplog):
    request = make_request()
    exc = RuntimeError("Sensitive internal database detail")

    with caplog.at_level(logging.ERROR):
        response = __import__("asyncio").run(
            unexpected_exception_handler(request, exc)
        )

    body = json.loads(response.body)

    assert response.status_code == 500
    assert body["error"] == "internal_server_error"
    assert body["message"] == (
        "An unexpected error occurred. Please try again later."
    )
    assert "Sensitive internal database detail" not in response.body.decode()
    assert "Sensitive internal database detail" in caplog.text
