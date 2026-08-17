#!/usr/bin/env python3
"""Serve the book-grounded LLM access layer over HTTP/JSON."""

from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from llm_service import BookLLMService


def first(values: list[str] | None, default: str = "") -> str:
    return values[0] if values else default


def api_description() -> dict:
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "What Power-Network Models Preserve — book-grounded LLM access",
            "version": "0.1.0",
            "description": "Read-only access to the versioned corpus, with source validation and explicit abstention.",
        },
        "paths": {
            "/healthz": {"get": {"responses": {"200": {"description": "Service and corpus health"}}}},
            "/v1/manifest": {"get": {"responses": {"200": {"description": "Corpus release identity"}}}},
            "/v1/search": {"get": {"parameters": [{"name": "query", "in": "query", "required": True}, {"name": "method", "in": "query", "schema": {"enum": ["lexical", "char_tfidf", "hybrid", "graph"]}}]}},
            "/v1/context": {"get": {"parameters": [{"name": "query", "in": "query", "required": True}, {"name": "audience", "in": "query"}, {"name": "method", "in": "query", "schema": {"enum": ["lexical", "char_tfidf", "hybrid", "graph"]}}]}, "post": {"description": "JSON body with query, audience, limit, method"}},
        },
    }


class AccessHandler(BaseHTTPRequestHandler):
    server_version = "multi-graph-book-llm/0.1"

    @property
    def service(self) -> BookLLMService:
        return self.server.book_service  # type: ignore[attr-defined]

    def log_message(self, format: str, *args) -> None:
        sys.stderr.write(f"[llm-http] {format % args}\n")

    def _send(self, status: int, payload, content_type: str = "application/json") -> None:
        if isinstance(payload, str):
            body = payload.encode("utf-8")
        else:
            body = (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status: int, message: str) -> None:
        self._send(status, {"error": message, "api_schema_version": "0.1.0"})

    def _response_format(self, query: dict[str, list[str]]) -> str:
        return first(query.get("format"), "json").lower()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        try:
            if parsed.path == "/healthz":
                self._send(200, self.service.health())
                return
            if parsed.path == "/v1/manifest":
                self._send(200, {
                    "api_schema_version": "0.1.0",
                    "corpus_id": self.service.index.manifest["corpus_id"],
                    "release": self.service.index.manifest["release"],
                    "record_count": self.service.index.manifest["record_count"],
                })
                return
            if parsed.path == "/openapi.json":
                self._send(200, api_description())
                return
            if parsed.path == "/v1/search":
                result = self.service.search(
                    first(query.get("query")),
                    int(first(query.get("limit"), "8")),
                    first(query.get("method"), "hybrid"),
                )
                if self._response_format(query) == "markdown":
                    lines = [f"# Book search results", "", f"**Query:** {result['query']}", ""]
                    lines.extend(
                        f"{position}. `{item['record_id']}` — {item['title']} ({item['source']['path']})"
                        for position, item in enumerate(result["results"], start=1)
                    )
                    self._send(200, "\n".join(lines) + "\n", "text/markdown")
                else:
                    self._send(200, result)
                return
            if parsed.path == "/v1/context":
                result = self.service.response(
                    first(query.get("query")),
                    first(query.get("audience"), "student"),
                    int(first(query.get("limit"), "6")),
                    first(query.get("method"), "hybrid"),
                )
                if self._response_format(query) == "markdown":
                    self._send(200, result["markdown"], "text/markdown")
                else:
                    self._send(200, result)
                return
            self._error(404, "unknown route")
        except (ValueError, TypeError, KeyError) as error:
            self._error(400, str(error))
        except Exception as error:  # keep internal details out of normal API responses
            self.log_message("internal error: %s", error)
            self._error(500, "internal service error")

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/v1/context":
            self._error(404, "unknown route")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 1_000_000:
                raise ValueError("request body is too large")
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("request body must be a JSON object")
            result = self.service.response(
                str(payload.get("query", "")),
                str(payload.get("audience", "student")),
                int(payload.get("limit", 6)),
                str(payload.get("method", "hybrid")),
            )
            accepts = self.headers.get("Accept", "application/json")
            if "text/markdown" in accepts:
                self._send(200, result["markdown"], "text/markdown")
            else:
                self._send(200, result)
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
            self._error(400, str(error))
        except Exception as error:
            self.log_message("internal error: %s", error)
            self._error(500, "internal service error")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    server = ThreadingHTTPServer((args.host, args.port), AccessHandler)
    server.book_service = BookLLMService()  # type: ignore[attr-defined]
    print(f"book LLM access server listening on http://{args.host}:{args.port}", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
