#!/usr/bin/env python3
"""Exercise the JSON, Markdown, HTTP, and MCP access routes."""

from __future__ import annotations

import json
import io
import sys
import subprocess
from types import SimpleNamespace

from llm_service import BookLLMService
from mcp_llm_server import handle_request
from serve_llm_access import AccessHandler

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]


def check(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    service = BookLLMService()
    packet_response = service.response("Do loads belong in Ybus?", "power_engineer")
    packet = packet_response["packet"]
    check(packet_response["validation"]["valid"], "direct response validation failed", errors)
    check(packet["status"] == "qualified", "dangerous-shortcut query was not qualified", errors)
    check("required qualifications" in packet_response["markdown"].lower(), "Markdown omitted qualification heading", errors)
    check(packet["sources"], "context packet has no sources", errors)
    unsupported = service.response("What is the weather on Mars?", "student")
    check(unsupported["packet"]["status"] == "unsupported", "unsupported query did not abstain", errors)
    under_retrieved = service.response(
        "Does a matching bus-matrix export establish that two studies have the same assets, ratings, and controls?",
        "power_engineer",
    )
    check(
        under_retrieved["packet"]["status"] == "under_retrieved",
        "supported-but-unqualified query did not expose under_retrieved status",
        errors,
    )
    check(
        "retrieval warning" in under_retrieved["markdown"].lower(),
        "under_retrieved Markdown omitted its warning",
        errors,
    )

    def exercise_http(method: str, path: str, body: bytes = b"", accept: str = "application/json") -> tuple[int, object]:
        captured: dict = {}
        handler = AccessHandler.__new__(AccessHandler)
        handler.server = SimpleNamespace(book_service=service)
        handler.path = path
        handler._send = lambda status, payload, content_type="application/json": captured.update(
            status=status, payload=payload, content_type=content_type
        )
        handler._error = lambda status, message: captured.update(
            status=status, payload={"error": message}, content_type="application/json"
        )
        handler.headers = {"Content-Length": str(len(body)), "Accept": accept}
        handler.rfile = io.BytesIO(body)
        if method == "GET":
            handler.do_GET()
        else:
            handler.do_POST()
        return captured["status"], captured["payload"]

    status, health = exercise_http("GET", "/healthz")
    check(status == 200 and health["status"] == "ok", "HTTP health route failed", errors)
    status, openapi = exercise_http("GET", "/openapi.json")
    check(status == 200 and openapi["openapi"] == "3.1.0", "OpenAPI route failed", errors)
    status, markdown = exercise_http("GET", "/v1/context?query=Do%20loads%20belong%20in%20Ybus%3F&audience=student&format=markdown")
    check(status == 200 and "Book-grounded answer packet" in markdown, "HTTP Markdown route failed", errors)
    status, posted = exercise_http(
        "POST", "/v1/context", json.dumps({"query": "Do loads belong in Ybus?", "audience": "power_engineer"}).encode()
    )
    check(status == 200 and posted["packet"]["release"] == packet["release"], "HTTP JSON route changed release identity", errors)
    graph_response = service.response("Should a topology API expose one adjacency list as the complete network graph?", "software_engineer", method="graph")
    check(graph_response["packet"]["retrieval"]["method"] == "graph_with_contract_expansion", "graph route was not exposed as an opt-in method", errors)

    initialize = handle_request(service, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25"}})
    check(initialize["result"]["serverInfo"]["name"] == "multi-graph-book", "MCP initialize failed", errors)
    tools = handle_request(service, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    check({tool["name"] for tool in tools["result"]["tools"]} == {"book_context", "book_search"}, "MCP tool list drifted", errors)
    called = handle_request(
        service,
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "book_context", "arguments": {"query": "Do loads belong in Ybus?"}},
        },
    )
    check(called["result"]["structuredContent"]["packet"]["status"] == "qualified", "MCP context call failed", errors)

    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25"}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "book_search", "arguments": {"query": "Ybus"}}},
    ]
    process = subprocess.run(
        [sys.executable, str(ROOT / "scripts/mcp_llm_server.py")],
        input="\n".join(json.dumps(message) for message in messages) + "\n",
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
        check=False,
    )
    check(process.returncode == 0, f"MCP stdio server exited {process.returncode}: {process.stderr}", errors)
    output_lines = [line for line in process.stdout.splitlines() if line.strip()]
    check(len(output_lines) == 3, "MCP stdio server returned the wrong response count", errors)
    if len(output_lines) == 3:
        parsed = [json.loads(line) for line in output_lines]
        check(parsed[2]["result"]["structuredContent"]["type"] == "book_search_results", "MCP stdio search failed", errors)

    if errors:
        print("LLM access-route check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("LLM access routes: direct packet, Markdown, HTTP JSON, and MCP stdio pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
