#!/usr/bin/env python3
"""Minimal newline-delimited MCP stdio adapter for the book LLM service."""

from __future__ import annotations

import json
import sys
from typing import Any

from llm_service import BookLLMService

MCP_PROTOCOL_VERSION = "2025-11-25"
SUPPORTED_PROTOCOL_VERSIONS = {MCP_PROTOCOL_VERSION, "2025-06-18"}
SERVER_NAME = "multi-graph-book"
SERVER_VERSION = "0.1.0"
MANIFEST_URI = "book://multi-graph-book/manifest"


def response(request_id: Any, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error_response(request_id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def tool_definitions() -> list[dict]:
    return [
        {
            "name": "book_context",
            "description": (
                "Retrieve a book-grounded answer packet. The result contains the supported answer basis, "
                "scope, qualifications, failure consequences, stable sources, and explicit abstention status."
            ),
            "inputSchema": {
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {"type": "string", "minLength": 1},
                    "audience": {"type": "string", "enum": ["student", "software_engineer", "power_engineer"]},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                    "method": {"type": "string", "enum": ["lexical", "char_tfidf", "hybrid", "graph"]},
                },
            },
        },
        {
            "name": "book_search",
            "description": "Search the versioned book corpus and return stable source-linked records.",
            "inputSchema": {
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {"type": "string", "minLength": 1},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                    "method": {"type": "string", "enum": ["lexical", "char_tfidf", "hybrid", "graph"]},
                },
            },
        },
    ]


def manifest_resource(service: BookLLMService) -> dict:
    return {
        "uri": MANIFEST_URI,
        "name": "Book corpus manifest",
        "description": "Release identity and record count for the book-grounded corpus.",
        "mimeType": "application/json",
    }


def handle_request(service: BookLLMService, request: dict) -> dict | None:
    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params") or {}
    if not isinstance(params, dict):
        return error_response(request_id, -32602, "params must be an object")
    if method == "initialize":
        requested = params.get("protocolVersion")
        protocol = requested if requested in SUPPORTED_PROTOCOL_VERSIONS else MCP_PROTOCOL_VERSION
        return response(
            request_id,
            {
                "protocolVersion": protocol,
                "capabilities": {"tools": {"listChanged": False}, "resources": {"subscribe": False, "listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                "instructions": "Use book_context for qualified answers; do not treat retrieval relevance as proof.",
            },
        )
    if method in {"notifications/initialized", "notifications/cancelled"}:
        return None
    if method == "ping":
        return response(request_id, {})
    if method == "tools/list":
        return response(request_id, {"tools": tool_definitions()})
    if method == "resources/list":
        return response(request_id, {"resources": [manifest_resource(service)]})
    if method == "resources/read":
        if params.get("uri") != MANIFEST_URI:
            return error_response(request_id, -32002, "unknown resource URI")
        return response(
            request_id,
            {
                "contents": [
                    {
                        **manifest_resource(service),
                        "text": json.dumps(service.health(), indent=2, ensure_ascii=False),
                    }
                ]
            },
        )
    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if not isinstance(arguments, dict):
            return error_response(request_id, -32602, "tool arguments must be an object")
        try:
            if name == "book_context":
                result = service.response(
                    str(arguments.get("query", "")),
                    str(arguments.get("audience", "student")),
                    int(arguments.get("limit", 6)),
                    str(arguments.get("method", "hybrid")),
                )
                return response(
                    request_id,
                    {"content": [{"type": "text", "text": result["markdown"]}], "structuredContent": result},
                )
            if name == "book_search":
                result = service.search(
                    str(arguments.get("query", "")),
                    int(arguments.get("limit", 8)),
                    str(arguments.get("method", "hybrid")),
                )
                return response(
                    request_id,
                    {
                        "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}],
                        "structuredContent": result,
                    },
                )
            return error_response(request_id, -32602, f"unknown tool: {name}")
        except (ValueError, TypeError, KeyError) as error:
            return response(
                request_id,
                {"isError": True, "content": [{"type": "text", "text": str(error)}]},
            )
    return error_response(request_id, -32601, f"method not found: {method}")


def main() -> int:
    service = BookLLMService()
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            if not isinstance(request, dict):
                raise ValueError("MCP message must be a JSON object")
            result = handle_request(service, request)
        except (json.JSONDecodeError, ValueError, TypeError) as error:
            result = error_response(None, -32700, str(error))
        if result is not None:
            sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
