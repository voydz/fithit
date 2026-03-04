from __future__ import annotations

import io
import urllib.error
from typing import Any

import fithitcli.parse as parse_module


class _FakeResponse:
    def __init__(
        self,
        *,
        status: int = 200,
        headers: dict[str, str] | None = None,
        url: str = "https://example.test/",
        body: bytes = b"",
    ) -> None:
        self.status = status
        self._headers = headers or {}
        self._url = url
        self._body = body

    @property
    def headers(self) -> dict[str, str]:
        return self._headers

    def getcode(self) -> int:
        return self.status

    def geturl(self) -> str:
        return self._url

    def read(self, n: int = -1) -> bytes:
        if n < 0:
            return self._body
        return self._body[:n]

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        return None


def _http_error(url: str, code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(url, code, "err", {}, io.BytesIO(b""))


def test_check_link_works_uses_get_status_code(monkeypatch):
    calls: list[str] = []

    def fake_urlopen(req, timeout=10):
        calls.append(req.get_method())
        return _FakeResponse(
            status=200,
            headers={"Content-Type": "text/html"},
            url="https://example.test/workout/123",
        )

    monkeypatch.setattr(parse_module.urllib.request, "urlopen", fake_urlopen)

    assert parse_module._check_link_works("https://example.test/workout/123", 5) is True
    assert calls == ["GET"]


def test_check_link_works_returns_false_on_get_404(monkeypatch):
    def fake_urlopen(req, timeout=10):
        raise _http_error(req.full_url, 404)

    monkeypatch.setattr(parse_module.urllib.request, "urlopen", fake_urlopen)

    assert parse_module._check_link_works("https://example.test/missing", 5) is False


def test_check_link_works_retries_on_429_then_passes(monkeypatch):
    calls: list[str] = []
    state = {"n": 0}

    def fake_urlopen(req, timeout=10):
        calls.append(req.get_method())
        state["n"] += 1
        if state["n"] == 1:
            raise _http_error(req.full_url, 429)
        return _FakeResponse(status=200)

    monkeypatch.setattr(parse_module.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(parse_module.time, "sleep", lambda _: None)

    assert parse_module._check_link_works("https://example.test/workout/123", 5) is True
    assert calls == ["GET", "GET"]


def test_check_link_works_returns_false_on_non_retryable_error(monkeypatch):
    calls: list[str] = []

    def fake_urlopen(req, timeout=10):
        calls.append(req.get_method())
        raise _http_error(req.full_url, 405)

    monkeypatch.setattr(parse_module.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(parse_module.time, "sleep", lambda _: None)

    assert parse_module._check_link_works("https://example.test/workout/123", 5) is False
    assert calls == ["GET"]
