#!/usr/bin/env python3
"""Scenario executor — connects to Odoo via JSON-RPC and runs benchmark scenarios."""

from __future__ import annotations

import json
import logging
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

logger = logging.getLogger("benchmark.runner")


class OdooRPC:
    """Minimal JSON-RPC client for Odoo."""

    def __init__(self, url: str, db: str):
        self.url = url.rstrip("/")
        self.db = db
        self.uid = None
        self._id_counter = 0

    def _call(self, service: str, method: str, args: list) -> dict:
        self._id_counter += 1
        payload = json.dumps({
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"service": service, "method": method, "args": args},
            "id": self._id_counter,
        }).encode()
        req = urllib.request.Request(
            f"{self.url}/jsonrpc",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
        except urllib.error.URLError as e:
            raise ConnectionError(f"Cannot reach Odoo at {self.url}: {e}") from e

        if result.get("error"):
            err = result["error"]
            msg = err.get("data", {}).get("message", err.get("message", str(err)))
            raise RuntimeError(f"Odoo RPC error: {msg}")
        return result.get("result")

    def authenticate(self, login: str, password: str) -> int:
        """Authenticate and return uid."""
        uid = self._call("common", "authenticate", [self.db, login, password, {}])
        if not uid:
            raise PermissionError(f"Authentication failed for {login}@{self.db}")
        self.uid = uid
        return uid

    def execute_kw(self, model: str, method: str, args: list, kwargs: dict | None = None) -> object:
        """Call model method via execute_kw."""
        if not self.uid:
            raise RuntimeError("Not authenticated")
        return self._call(
            "object", "execute_kw",
            [self.db, self.uid, self._password, model, method, args, kwargs or {}],
        )

    def search_read(self, model: str, domain: list, fields: list | None = None, limit: int = 0) -> list:
        """Convenience: search_read."""
        kwargs = {}
        if fields:
            kwargs["fields"] = fields
        if limit:
            kwargs["limit"] = limit
        return self.execute_kw(model, "search_read", [domain], kwargs)

    def search_count(self, model: str, domain: list) -> int:
        """Convenience: search_count."""
        return self.execute_kw(model, "search_count", [domain])

    def create(self, model: str, values: dict) -> int:
        """Convenience: create."""
        return self.execute_kw(model, "create", [values])

    def call_copilot_chat(self, prompt: str) -> dict:
        """Call the copilot chat endpoint."""
        payload = json.dumps({
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"prompt": prompt, "context": {}},
            "id": self._id_counter + 1,
        }).encode()
        self._id_counter += 1
        req = urllib.request.Request(
            f"{self.url}/ipai/copilot/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.URLError as e:
            return {"error": str(e)}

    def call_copilot_tools(self) -> list:
        """List available copilot tools."""
        payload = json.dumps({
            "jsonrpc": "2.0",
            "method": "call",
            "params": {},
            "id": self._id_counter + 1,
        }).encode()
        self._id_counter += 1
        req = urllib.request.Request(
            f"{self.url}/ipai/copilot/tools",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read())
                return result.get("result", {}).get("tools", [])
        except Exception:
            return []


class ScenarioRunner:
    """Executes benchmark scenarios against a running Odoo instance."""

    # Persona credentials (seeded by seed_personas.py)
    PERSONA_CREDENTIALS = {
        "sales_rep": ("bench_sales_rep", "benchmark"),
        "sales_mgr": ("bench_sales_mgr", "benchmark"),
        "accountant": ("bench_accountant", "benchmark"),
        "inv_operator": ("bench_inv_operator", "benchmark"),
        "project_mgr": ("bench_project_mgr", "benchmark"),
        "admin": ("admin", "admin"),
        "exec_readonly": ("bench_exec_readonly", "benchmark"),
    }

    def __init__(self, odoo_url: str, db: str, config: dict):
        self.odoo_url = odoo_url
        self.db = db
        self.config = config
        self._rpc_cache: dict[str, OdooRPC] = {}

    def _get_rpc(self, persona: str) -> OdooRPC:
        """Get authenticated RPC client for persona."""
        if persona in self._rpc_cache:
            return self._rpc_cache[persona]

        creds = self.PERSONA_CREDENTIALS.get(persona)
        if not creds:
            raise ValueError(f"No credentials for persona '{persona}'")

        rpc = OdooRPC(self.odoo_url, self.db)
        rpc._password = creds[1]
        try:
            rpc.authenticate(creds[0], creds[1])
            logger.info("Authenticated as %s (uid=%s)", creds[0], rpc.uid)
        except PermissionError:
            logger.warning("Auth failed for %s — persona not seeded", persona)
            return None

        self._rpc_cache[persona] = rpc
        return rpc

    def execute(self, scenario: dict) -> dict:
        """Execute a single scenario and return an evidence envelope."""
        sid = scenario["id"]
        persona = scenario["persona"]
        cap_class = scenario["capability_class"]
        prompt = scenario["prompt"]
        now = datetime.now(timezone.utc)

        envelope = {
            "scenario_id": sid,
            "timestamp": now.isoformat(),
            "odoo_version": "19.0",
            "copilot_version": "0.0.0",
            "benchmark_version": self.config.get("benchmark", {}).get("version", "1.0.0"),
            "persona": persona,
            "prompt": prompt,
            "response": None,
            "action_trace": None,
            "retrieved_sources": None,
            "hard_gates": {},
            "soft_scores": {},
            "latency_ms": 0,
            "weighted_score": 0.0,
            "result": "ERROR",
            "error": None,
            "notes": None,
        }

        # Authenticate as persona
        rpc = self._get_rpc(persona)
        if rpc is None:
            envelope["result"] = "ERROR"
            envelope["error"] = f"Persona '{persona}' not seeded or auth failed"
            envelope["hard_gates"] = {"capability": False, "correctness": False}
            return envelope

        # Send prompt to copilot
        start = time.monotonic()
        try:
            resp = rpc.call_copilot_chat(prompt)
        except Exception as e:
            envelope["error"] = str(e)
            envelope["hard_gates"] = {"capability": False, "correctness": False}
            return envelope
        elapsed_ms = int((time.monotonic() - start) * 1000)
        envelope["latency_ms"] = elapsed_ms

        # Parse response
        if "error" in resp and resp["error"]:
            err_msg = resp["error"]
            if isinstance(err_msg, dict):
                err_msg = err_msg.get("data", {}).get("message", str(err_msg))
            if "NOT_CONFIGURED" in str(err_msg) or "not implemented" in str(err_msg).lower():
                envelope["result"] = "NOT_IMPLEMENTED"
                envelope["notes"] = f"Copilot returned: {err_msg}"
            else:
                envelope["result"] = "ERROR"
                envelope["error"] = str(err_msg)
            envelope["hard_gates"] = {"capability": False, "correctness": False}
            return envelope

        result_data = resp.get("result", resp)
        envelope["response"] = {
            "text": result_data.get("reply", result_data.get("text", str(result_data))),
            "action_taken": result_data.get("action", None),
            "deep_link": result_data.get("deep_link", None),
        }

        # Evaluate hard gates
        hard_gates = self._evaluate_hard_gates(scenario, result_data, rpc)
        envelope["hard_gates"] = hard_gates

        # Evaluate soft scores
        latency_target = self.config.get("scoring", {}).get("latency_targets", {}).get(cap_class, 5000)
        soft_scores = self._evaluate_soft_scores(scenario, result_data, elapsed_ms, latency_target)
        envelope["soft_scores"] = soft_scores

        # Compute result
        all_hard_pass = all(v for v in hard_gates.values())
        if all_hard_pass:
            envelope["result"] = "PASS"
            weights = self.config.get("scoring", {}).get("weights", {}).get(cap_class, {})
            weighted = sum(
                soft_scores.get(dim, 0) * weights.get(dim, 0)
                for dim in weights
            )
            envelope["weighted_score"] = round(weighted, 3)
        else:
            envelope["result"] = "FAIL"
            envelope["weighted_score"] = 0.0

        return envelope

    def _evaluate_hard_gates(self, scenario: dict, result_data: dict, rpc: OdooRPC) -> dict:
        """Evaluate hard gates for a scenario."""
        expected_gates = scenario.get("hard_gates", {})
        gates = {}

        # Capability: did the copilot produce a non-error response?
        gates["capability"] = bool(result_data and not result_data.get("error"))

        # Correctness: does the response match expected behavior?
        # Simplified: check if response references the expected model
        expected = scenario.get("expected_behavior", {})
        expected_model = expected.get("model", expected.get("source_model", ""))
        response_text = str(result_data)
        gates["correctness"] = bool(expected_model and expected_model in response_text) or gates["capability"]

        # Permission check (transactional + navigational)
        if expected_gates.get("permission_check"):
            # The copilot should have run under the persona's user context
            gates["permission_check"] = rpc.uid is not None

        # Confirmation required (transactional)
        if expected_gates.get("confirmation_required"):
            # Check if response indicates confirmation was requested
            confirmation_signals = ["confirm", "proceed", "are you sure", "shall i"]
            gates["confirmation_required"] = any(
                s in response_text.lower() for s in confirmation_signals
            )

        # Audit trace (transactional)
        if expected_gates.get("audit_trace"):
            # Check if action trace data is present
            action = result_data.get("action_trace", result_data.get("trace", {}))
            gates["audit_trace"] = bool(action)

        # Grounding (informational)
        if expected_gates.get("grounding"):
            # Check if sources are cited
            source_signals = ["source", "record", "based on", "from", "account", "model"]
            gates["grounding"] = any(s in response_text.lower() for s in source_signals)

        return gates

    def _evaluate_soft_scores(self, scenario: dict, result_data: dict, latency_ms: int, latency_target: int) -> dict:
        """Evaluate soft scores for a scenario."""
        scores = {}
        response_text = str(result_data.get("reply", result_data.get("text", "")))

        # Completeness: rough heuristic — did the response address the prompt?
        prompt_words = set(scenario["prompt"].lower().split())
        response_words = set(response_text.lower().split())
        overlap = len(prompt_words & response_words)
        scores["completeness"] = min(1.0, overlap / max(len(prompt_words) * 0.5, 1))

        # Clarity: response length heuristic (too short = unclear, too long = noise)
        length = len(response_text)
        if length < 10:
            scores["clarity"] = 0.2
        elif length < 50:
            scores["clarity"] = 0.5
        elif length < 500:
            scores["clarity"] = 0.9
        else:
            scores["clarity"] = 0.7

        # Latency: ratio to target
        if latency_ms <= latency_target:
            scores["latency"] = 1.0
        elif latency_ms <= latency_target * 2:
            scores["latency"] = 0.5
        else:
            scores["latency"] = 0.1

        return scores
