#!/usr/bin/env python3
"""Read-only diagnostic probes for the October scientific review.

Print observations, not pass/fail judgements or measured agent results.
Run from any directory; redirect stdout to retain a fresh JSON snapshot.
"""

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from llm_service import BookLLMService
from mcp_llm_server import handle_request

QUERIES = [
    "Does a zero terminal voltage make power balance equivalent to KCL?",
    "Can a small transformer leakage be rounded to zero in ybus_augmented?",
    "Does ybus_linearized fold all compute a Jacobian?",
    "Can I merge two buses because their GPS coordinates coincide?",
    "Are three delta terminals three independent load coils?",
    "Can I reuse an OPF after updating a parameter through zero?",
    "Does a passed solved_network_feasibility_validation recompute every device equation?",
    "Can I replace a small impedance by an ideal switch without changing current sharing?",
]


def main():
    service = BookLLMService()
    observations = []
    for query in QUERIES:
        result = service.response(query)
        packet = result["packet"]
        observations.append({
            "query": query,
            "status": packet["status"],
            "routes": packet["retrieval"]["detected_misconceptions"],
            "direct_answer_basis": packet["answer_contract"]["direct_answer_basis"],
            "required_qualifications": packet["answer_contract"]["required_qualifications"],
            "mandatory_record_ids": [r["record_id"] for r in packet["mandatory_records"]],
            "validation": result["validation"],
        })
    probes = []
    requests = [
        ("null query", {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
            "name": "book_search", "arguments": {"query": None}}}),
        ("fractional limit", {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
            "name": "book_search", "arguments": {"query": "parallel branches", "limit": 1.9}}}),
        ("unknown notification", {"jsonrpc": "2.0", "method": "notifications/progress", "params": {
            "progressToken": 1, "progress": 1}}),
        ("modern discovery", {"jsonrpc": "2.0", "id": 3, "method": "server/discover"}),
    ]
    for label, request in requests:
        response = handle_request(service, request)
        item = {"probe": label, "request": request, "responded": response is not None}
        if response is not None:
            result = response.get("result", {})
            payload = result.get("structuredContent", {})
            item.update(error=response.get("error"), is_error=result.get("isError", False),
                        interpreted_query=payload.get("query"), result_count=len(payload.get("results", [])))
        probes.append(item)
    pair = json.loads((ROOT / "generated/federated-knowledge-pair-manifest.json").read_text())
    print(json.dumps({
        "evidence_class": "targeted_diagnostic_observations_not_agent_benchmark",
        "book_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "corpus_manifest_sha256": hashlib.sha256((ROOT / "llm/generated/corpus-manifest.json").read_bytes()).hexdigest(),
        "pair_sha256": pair["pair_sha256"],
        "retrieval": observations,
        "mcp": probes,
    }, indent=2))


if __name__ == "__main__":
    main()
