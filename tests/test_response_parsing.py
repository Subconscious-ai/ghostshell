import httpx
import pytest

from server.tools._core.exceptions import ValidationError
from server.tools._core.handlers import _parse_response_payload


def test_parse_response_payload_preserves_json():
    response = httpx.Response(200, json={"is_causal": True})

    assert _parse_response_payload(response) == {"is_causal": True}


def test_parse_response_payload_returns_final_sse_result_data():
    body = "\n\n".join(
        [
            'data: {"type":"progress","step":"checking"}',
            'data: {"type":"result","data":{"is_causal":true,"suggestions":[]}}',
        ]
    )
    response = httpx.Response(
        200,
        text=body,
        headers={"content-type": "text/event-stream; charset=utf-8"},
    )

    assert _parse_response_payload(response) == {
        "is_causal": True,
        "suggestions": [],
    }


def test_parse_response_payload_rejects_sse_without_result():
    response = httpx.Response(
        200,
        text='data: {"type":"progress","step":"checking"}\n\n',
        headers={"content-type": "text/event-stream"},
    )

    with pytest.raises(ValidationError, match="final result"):
        _parse_response_payload(response)
