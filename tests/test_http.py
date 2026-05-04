import http.client
import urllib.request

import pytest

from minigeo.rag.http import post_json


class _FakeResponse:
    def __init__(self, body: bytes | BaseException):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self) -> bytes:
        if isinstance(self.body, BaseException):
            raise self.body
        return self.body


def test_post_json_retries_incomplete_response(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"count": 0}

    def fake_urlopen(request: urllib.request.Request, timeout: float):
        calls["count"] += 1
        if calls["count"] == 1:
            return _FakeResponse(http.client.IncompleteRead(b'{"ok"', 12))
        return _FakeResponse(b'{"ok": true}')

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    assert post_json("http://localhost:8000/v1/test", {}, {"input": "石英"}, 1.0) == {"ok": True}
    assert calls["count"] == 2


def test_post_json_reports_incomplete_response_after_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: urllib.request.Request, timeout: float):
        return _FakeResponse(http.client.IncompleteRead(b'{"ok"', 12))

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="incomplete response"):
        post_json("http://localhost:8000/v1/test", {}, {"input": "石英"}, 1.0)
