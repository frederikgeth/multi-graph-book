#!/usr/bin/env python3
"""Regression checks for the book's legacy and modern MCP request boundaries."""

import json
from pathlib import Path
import subprocess
import sys
import unittest

from llm_service import BookLLMService
from mcp_llm_server import handle_request, MANIFEST_URI, META_PREFIX, MODERN_PROTOCOL_VERSION

ROOT = Path(__file__).resolve().parents[1]


class MCPRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = BookLLMService()

    def call(self, arguments, name="book_search"):
        return handle_request(self.service, {
            "jsonrpc": "2.0", "id": "request-1", "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        })

    def test_invalid_arguments_are_request_errors(self):
        invalid = [
            None, [], False, {}, {"query": None}, {"query": 42}, {"query": []},
            {"query": ""}, {"query": "  "},
            *({"query": "parallel", "limit": v} for v in [True, "2", 1.9, 0, 21, None]),
            {"query": "parallel", "method": []},
            {"query": "parallel", "method": "neural"},
            {"query": "parallel", "audience": "student"},  # not a search argument
            {"query": "parallel", "unknown": True},
        ]
        for arguments in invalid:
            with self.subTest(arguments=arguments):
                response = self.call(arguments)
                self.assertEqual(response["error"]["code"], -32602)
                self.assertEqual(response["id"], "request-1")
                self.assertNotIn("result", response)
        for audience in ([], None, "expert"):
            self.assertEqual(self.call({"query": "parallel", "audience": audience},
                                       "book_context")["error"]["code"], -32602)
        for name in (None, [], "missing"):
            self.assertEqual(self.call({"query": "parallel"}, name)["error"]["code"], -32602)

    def test_valid_arguments_preserve_service_behavior(self):
        for limit in (1, 1.0, 20):  # JSON Schema integer also admits integral numbers
            with self.subTest(limit=limit):
                result = self.call({"query": "parallel", "limit": limit})["result"]
                self.assertEqual(result["structuredContent"], self.service.search("parallel", int(limit)))
        result = self.call({"query": "Do loads belong in Ybus?"}, "book_context")["result"]
        self.assertEqual(result["structuredContent"]["packet"]["status"], "qualified")
        refused = self.call({"query": "Can I reuse an OPF after updating a parameter through zero?"},
                            "book_context")["result"]
        self.assertEqual(refused["structuredContent"]["packet"]["status"], "under_retrieved")
        self.assertFalse(refused.get("isError", False))

    def test_notifications_do_not_reply_or_execute(self):
        # A missing service ensures a tool notification cannot execute a query.
        for method in ("notifications/initialized", "notifications/cancelled",
                       "notifications/progress", "notifications/unknown", "tools/call"):
            with self.subTest(method=method):
                self.assertIsNone(handle_request(None, {
                    "jsonrpc": "2.0", "method": method,
                    "params": {"name": "book_search", "arguments": {"query": "parallel"}},
                }))

    def test_malformed_envelopes_and_params(self):
        for request in (None, [], 4, {}, {"jsonrpc": "1.0", "id": 4, "method": "ping"},
                        {"jsonrpc": "2.0", "id": 4, "method": []}):
            with self.subTest(request=request):
                self.assertEqual(handle_request(self.service, request)["error"]["code"], -32600)
        for request_id in (None, True, 1.5, [], {}):
            response = handle_request(self.service, {"jsonrpc": "2.0", "id": request_id, "method": "ping"})
            self.assertEqual(response["error"]["code"], -32600)
            self.assertIsNone(response["id"])
        for params in (None, [], False):
            self.assertEqual(handle_request(self.service, {
                "jsonrpc": "2.0", "id": 4, "method": "tools/list", "params": params,
            })["error"]["code"], -32602)

    def test_version_negotiation_and_invalid_versions(self):
        for requested, expected in [("2025-06-18", "2025-06-18"),
                                    ("2025-11-25", "2025-11-25"),
                                    ("2026-07-28", "2025-11-25"),  # initialize selects the legacy era
                                    ("2099-01-01", "2025-11-25")]:
            response = handle_request(self.service, {
                "jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {"protocolVersion": requested},
            })
            self.assertEqual(response["result"]["protocolVersion"], expected)
        for requested in (None, [], {}, True, ""):
            response = handle_request(self.service, {
                "jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {"protocolVersion": requested},
            })
            self.assertEqual(response["error"]["code"], -32602)

    def modern(self, method, params=None, version=MODERN_PROTOCOL_VERSION):
        return {"jsonrpc": "2.0", "id": "modern-1", "method": method,
                "params": {"_meta": {META_PREFIX + "protocolVersion": version,
                                      META_PREFIX + "clientCapabilities": {}}, **(params or {})}}

    def test_modern_discovery_and_cacheable_methods(self):
        for method, params, key in (
            ("server/discover", {}, "supportedVersions"),
            ("tools/list", {}, "tools"),
            ("resources/list", {}, "resources"),
            ("resources/templates/list", {}, "resourceTemplates"),
            ("resources/read", {"uri": MANIFEST_URI}, "contents"),
        ):
            with self.subTest(method=method):
                result = handle_request(self.service, self.modern(method, params))["result"]
                self.assertEqual(result["resultType"], "complete")
                self.assertEqual(result["cacheScope"], "private")
                self.assertEqual(result["ttlMs"], 0)
                self.assertEqual(result["_meta"][META_PREFIX + "serverInfo"]["name"], "multi-graph-book")
                self.assertIn(key, result)
        discover = handle_request(self.service, self.modern("server/discover"))["result"]
        self.assertEqual(discover["supportedVersions"], ["2026-07-28", "2025-11-25", "2025-06-18"])
        self.assertFalse(discover["capabilities"]["tools"]["listChanged"])
        self.assertFalse(discover["capabilities"]["resources"]["subscribe"])

    def test_modern_calls_preserve_scientific_status(self):
        for query, status in (
            ("Do loads belong in Ybus?", "qualified"),
            ("Does a zero terminal voltage make power balance equivalent to KCL?", "qualified"),
            ("Can I reuse an OPF after updating a parameter through zero?", "under_retrieved"),
            ("What is the weather on Mars?", "unsupported"),
        ):
            with self.subTest(status=status):
                result = handle_request(self.service, self.modern("tools/call", {
                    "name": "book_context", "arguments": {"query": query}}))["result"]
                self.assertEqual(result["structuredContent"], self.service.response(query))
                self.assertEqual(result["structuredContent"]["packet"]["status"], status)
                self.assertEqual(result["resultType"], "complete")
                self.assertNotIn("ttlMs", result)  # tool results are not cacheable protocol lists
                self.assertFalse(result.get("isError", False))

    def test_modern_version_errors_and_request_local_metadata(self):
        mismatch = handle_request(self.service, self.modern("tools/list", version="2099-01-01"))
        self.assertEqual(mismatch["error"]["code"], -32022)
        self.assertEqual(mismatch["error"]["data"]["requested"], "2099-01-01")
        self.assertIn(MODERN_PROTOCOL_VERSION, mismatch["error"]["data"]["supported"])
        for meta in (None, [], {}, {META_PREFIX + "protocolVersion": []},
                     {META_PREFIX + "protocolVersion": MODERN_PROTOCOL_VERSION},
                     {META_PREFIX + "protocolVersion": MODERN_PROTOCOL_VERSION, META_PREFIX + "clientCapabilities": []},
                     {META_PREFIX + "protocolVersion": MODERN_PROTOCOL_VERSION, META_PREFIX + "clientCapabilities": {},
                      META_PREFIX + "clientInfo": {"name": "missing version"}}):
            with self.subTest(meta=meta):
                malformed = self.modern("server/discover", {"_meta": meta})
                self.assertEqual(handle_request(self.service, malformed)["error"]["code"], -32602)
        # A previous valid call cannot supply missing capabilities for a later call.
        handle_request(self.service, self.modern("tools/list"))
        missing = self.modern("tools/list", {"_meta": {META_PREFIX + "protocolVersion": MODERN_PROTOCOL_VERSION}})
        self.assertEqual(handle_request(self.service, missing)["error"]["code"], -32602)
        for removed in ("initialize", "ping", "logging/setLevel", "resources/subscribe"):
            self.assertEqual(handle_request(self.service, self.modern(removed))["error"]["code"], -32601)
        resource = self.modern("resources/read", {"uri": "book://unknown"})
        self.assertEqual(handle_request(self.service, resource)["error"]["code"], -32602)
        del resource["params"]["_meta"]
        self.assertEqual(handle_request(self.service, resource)["error"]["code"], -32002)

    def test_mixed_eras_over_one_stdio_process(self):
        messages = [
            self.modern("server/discover"),
            {"jsonrpc": "2.0", "id": 2, "method": "initialize", "params": {"protocolVersion": "2025-11-25"}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/list"},
            self.modern("tools/list", version="2099-01-01"),
            self.modern("tools/list"),
            {"jsonrpc": "2.0", "id": 6, "method": "ping"},
        ]
        completed = subprocess.run([sys.executable, str(ROOT / "scripts/mcp_llm_server.py")],
                                   input="\n".join(map(json.dumps, messages)) + "\n", text=True,
                                   capture_output=True, check=True, timeout=30)
        replies = [json.loads(line) for line in completed.stdout.splitlines()]
        self.assertEqual(len(replies), 6)
        self.assertEqual(replies[0]["result"]["resultType"], "complete")
        self.assertEqual(replies[1]["result"]["protocolVersion"], "2025-11-25")
        self.assertNotIn("resultType", replies[2]["result"])
        self.assertEqual(replies[3]["error"]["code"], -32022)
        self.assertEqual(replies[4]["result"]["tools"], replies[2]["result"]["tools"])
        self.assertEqual(replies[5]["result"], {})

    def test_stdio_recovers_after_bad_messages_and_ignores_notifications(self):
        messages = [
            "{", "[]", '{"jsonrpc":"2.0","id":1,"method":"ping","params":{"n":NaN}}',
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "initialize",
                        "params": {"protocolVersion": "2025-11-25"}}),
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
            json.dumps({"jsonrpc": "2.0", "method": "notifications/unknown"}),
            json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                        "params": {"name": "book_search", "arguments": {"query": None}}}),
            json.dumps({"jsonrpc": "2.0", "id": 4, "method": "ping"}),
        ]
        completed = subprocess.run([sys.executable, str(ROOT / "scripts/mcp_llm_server.py")],
                                   input="\n".join(messages) + "\n", text=True,
                                   capture_output=True, check=True, timeout=30)
        replies = [json.loads(line) for line in completed.stdout.splitlines()]
        self.assertEqual(len(replies), 6)
        self.assertEqual([r["error"]["code"] for r in replies[:3]], [-32700, -32600, -32700])
        self.assertEqual(replies[3]["id"], 2)
        self.assertEqual(replies[4]["error"]["code"], -32602)
        self.assertEqual(replies[5], {"jsonrpc": "2.0", "id": 4, "result": {}})


if __name__ == "__main__":
    unittest.main()
