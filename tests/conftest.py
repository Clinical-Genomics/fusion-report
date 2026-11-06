"""Shared test fixtures."""

import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, List, Tuple

import pytest

from fusion_report.common import fetch
from fusion_report.common.singleton import Singleton

# (status, headers, body)
Response = Tuple[int, Dict[str, str], bytes]


class FakeServer:
    """Local HTTP server that answers each path with a queue of canned responses.

    The last response of a queue is repeated once the queue is exhausted.
    """

    def __init__(self) -> None:
        self.routes: Dict[str, List[Response]] = {}
        self.hits: Dict[str, int] = {}
        self.request_headers: List[Dict[str, str]] = []
        server = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802
                server.request_headers.append(dict(self.headers))
                path = self.path.split("?")[0]
                server.hits[path] = server.hits.get(path, 0) + 1
                queue = server.routes.get(path, [(404, {"Content-Type": "text/html"}, b"<html>")])
                status, headers, body = queue.pop(0) if len(queue) > 1 else queue[0]
                self.send_response(status)
                headers = {"Content-Length": str(len(body)), **headers}
                for key, value in headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.httpd.server_address[1]}{path}"

    def add(self, path: str, *responses: Response) -> str:
        self.routes[path] = list(responses)
        return self.url(path)

    def close(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()


@pytest.fixture
def http_server():
    server = FakeServer()
    yield server
    server.close()


@pytest.fixture(autouse=True)
def _fast_retries(monkeypatch):
    """No backoff sleeps in tests."""
    monkeypatch.setattr(fetch, "RETRY_BACKOFF", 0)


@pytest.fixture(autouse=True)
def _isolated_state(monkeypatch):
    """Restore the working directory and reset cached database singletons per test."""
    cwd = os.getcwd()
    monkeypatch.setattr(Singleton, "_instances", {})
    yield
    os.chdir(cwd)
