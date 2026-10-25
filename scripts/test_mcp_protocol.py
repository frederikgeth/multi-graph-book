#!/usr/bin/env python3
"""Regression checks for the book's legacy MCP request boundary."""

import json
from pathlib import Path
import subprocess
import sys
import unittest

from llm_service import BookLLMService
from mcp_llm_server import handle_request

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
        refused = self.call({"query": "Does a zero terminal voltage make power balance equivalent to KCL?"},
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
