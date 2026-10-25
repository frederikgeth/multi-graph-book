#!/usr/bin/env python3
"""Minimal newline-delimited MCP stdio adapter for the book LLM service."""

from __future__ import annotations

import json
import sys
from typing import Any

from llm_service import BookLLMService

MCP_PROTOCOL_VERSION = "2025-11-25"
LEGACY_PROTOCOL_VERSIONS = {MCP_PROTOCOL_VERSION, "2025-06-18"}
MODERN_PROTOCOL_VERSION = "2026-07-28"
SUPPORTED_PROTOCOL_VERSIONS = [MODERN_PROTOCOL_VERSION, MCP_PROTOCOL_VERSION, "2025-06-18"]
META_PREFIX = "io.modelcontextprotocol/"
SERVER_NAME = "multi-graph-book"
SERVER_VERSION = "0.2.0"
MANIFEST_URI = "book://multi-graph-book/manifest"
CACHEABLE_METHODS = {"server/discover", "tools/list", "resources/list", "resources/read", "resources/templates/list"}


def capabilities() -> dict:
    return {"tools": {"listChanged": False}, "resources": {"subscribe": False, "listChanged": False}}


def response(request_id: Any, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error_response(request_id: Any, code: int, message: str, data: dict | None = None) -> dict:
    error = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": error}


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
                "additionalProperties": False,
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
                "additionalProperties": False,
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
        "description": "Book corpus hashes, federated pair identity, and pinned executable revision; no live package inspection.",
        "mimeType": "application/json",
    }


def validate_tool_arguments(name: str, arguments: Any) -> None:
    """Check this adapter's flat schemas before any lossless normalization."""
    definitions = {tool["name"]: tool for tool in tool_definitions()}
    if name not in definitions:
        raise ValueError(f"unknown tool: {name}")
    if not isinstance(arguments, dict):
        raise ValueError("tool arguments must be an object")
    schema = definitions[name]["inputSchema"]
    for required in schema["required"]:
        if required not in arguments:
            raise ValueError(f"missing required argument: {required}")
    for key, value in arguments.items():
        rule = schema["properties"].get(key)
        if rule is None:
            raise ValueError(f"unknown argument: {key}")
        if rule["type"] == "string" and not isinstance(value, str):
            raise ValueError(f"{key} must be a string")
        # bool is a subclass of int in Python but is not a JSON Schema integer.
        if rule["type"] == "integer" and not (
            type(value) is int or (type(value) is float and value.is_integer())
        ):
            raise ValueError(f"{key} must be an integer")
        if "minLength" in rule and len(value.strip()) < rule["minLength"]:
            raise ValueError(f"{key} must not be empty")
        if "minimum" in rule and not rule["minimum"] <= value <= rule["maximum"]:
            raise ValueError(f"{key} must be between {rule['minimum']} and {rule['maximum']}")
        if "enum" in rule and value not in rule["enum"]:
            raise ValueError(f"unsupported {key}: {value}")


def handle_request(service: BookLLMService, request: Any) -> dict | None:
    if not isinstance(request, dict):
        return error_response(None, -32600, "MCP message must be a JSON object")
    method = request.get("method")
    request_id = request.get("id")
    if "id" in request and type(request_id) not in (str, int):
        return error_response(None, -32600, "request id must be a string or integer")
    if request.get("jsonrpc") != "2.0" or not isinstance(method, str) or not method:
        return error_response(request_id, -32600, "invalid JSON-RPC request envelope")
    # Notifications, including unrecognized ones, have no response. Do not
    # execute a tool sent without a request ID or emit an id:null reply.
    if "id" not in request:
        return None
    params = request.get("params", {})
    if not isinstance(params, dict):
        return error_response(request_id, -32602, "params must be an object")
    meta = params.get("_meta", {})
    if not isinstance(meta, dict):
        return error_response(request_id, -32602, "_meta must be an object")
    modern = method == "server/discover" or any(
        META_PREFIX + key in meta for key in ("protocolVersion", "clientCapabilities", "clientInfo")
    )
    if modern:
        version = meta.get(META_PREFIX + "protocolVersion")
        if not isinstance(version, str) or not version:
            return error_response(request_id, -32602, "modern requests require protocolVersion metadata")
        if version in LEGACY_PROTOCOL_VERSIONS:
            return error_response(request_id, -32602, "legacy versions require initialize, not modern request metadata")
        if version != MODERN_PROTOCOL_VERSION:
            return error_response(request_id, -32022, "Unsupported protocol version",
                                  {"supported": SUPPORTED_PROTOCOL_VERSIONS, "requested": version})
        if not isinstance(meta.get(META_PREFIX + "clientCapabilities"), dict):
            return error_response(request_id, -32602, "modern requests require clientCapabilities metadata")
        if META_PREFIX + "clientInfo" in meta:
            info = meta[META_PREFIX + "clientInfo"]
            if not isinstance(info, dict) or any(not isinstance(info.get(key), str) for key in ("name", "version")):
                return error_response(request_id, -32602, "clientInfo must contain string name and version")
        if method in {"initialize", "ping"}:
            return error_response(request_id, -32601, f"{method} is not a modern MCP method")
    result = dispatch(service, request_id, method, params, modern=modern)
    if modern and "result" in result:
        payload = result["result"]
        payload["resultType"] = "complete"
        payload["_meta"] = {META_PREFIX + "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION}}
        if method in CACHEABLE_METHODS:
            # No shared caching or promise of freshness for a mutable local checkout.
            payload.update(ttlMs=0, cacheScope="private")
    return result


def dispatch(service: BookLLMService, request_id: Any, method: str, params: dict, *, modern: bool) -> dict:
    """Map protocol methods to the shared service without changing evidence semantics."""
    if method == "server/discover":
        return response(request_id, {
            "supportedVersions": SUPPORTED_PROTOCOL_VERSIONS,
            "capabilities": capabilities(),
            "instructions": "Use book_context for qualified answers; the manifest identifies pinned exports, not a live executable runtime.",
        })
    if method == "initialize":
        requested = params.get("protocolVersion")
        if not isinstance(requested, str) or not requested:
            return error_response(request_id, -32602, "protocolVersion must be a nonempty string")
        protocol = requested if requested in LEGACY_PROTOCOL_VERSIONS else MCP_PROTOCOL_VERSION
        return response(
            request_id,
            {
                "protocolVersion": protocol,
                "capabilities": capabilities(),
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                "instructions": "Use book_context for qualified answers; do not treat retrieval relevance as proof.",
            },
        )
    if method == "ping":
        return response(request_id, {})
    if method == "tools/list":
        return response(request_id, {"tools": tool_definitions()})
    if method == "resources/list":
        return response(request_id, {"resources": [manifest_resource(service)]})
    if method == "resources/templates/list":
        return response(request_id, {"resourceTemplates": []})
    if method == "resources/read":
        if params.get("uri") != MANIFEST_URI:
            return error_response(request_id, -32602 if modern else -32002, "unknown resource URI")
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
        arguments = params.get("arguments", {})
        if not isinstance(name, str):
            return error_response(request_id, -32602, "tool name must be a string")
        try:
            validate_tool_arguments(name, arguments)
        except ValueError as error:
            return error_response(request_id, -32602, str(error))
        try:
            if name == "book_context":
                result = service.response(
                    arguments["query"],
                    arguments.get("audience", "student"),
                    int(arguments.get("limit", 6)),
                    arguments.get("method", "hybrid"),
                )
                return response(
                    request_id,
                    {"content": [{"type": "text", "text": result["markdown"]}], "structuredContent": result},
                )
            if name == "book_search":
                result = service.search(
                    arguments["query"],
                    int(arguments.get("limit", 8)),
                    arguments.get("method", "hybrid"),
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
            def reject_nonfinite(value: str) -> None:
                raise ValueError(f"invalid JSON number: {value}")

            request = json.loads(line, parse_constant=reject_nonfinite)
        except (json.JSONDecodeError, ValueError) as error:
            result = error_response(None, -32700, str(error))
        else:
            result = handle_request(service, request)
        if result is not None:
            sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
