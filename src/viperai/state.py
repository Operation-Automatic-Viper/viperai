# src/viperai/state.py
"""What the agent has learned so far, built up from tool results and fed to later steps."""
import json

from viperai.scope import in_scope

SUBDOMAIN_TOOLS = {"chaos", "sublistah"}


def new_state() -> dict:
    return {"subdomains": [], "live_hosts": [], "findings": []}


def _per_host(result: dict, default_host: str) -> list:
    """Normalise single-host and multi-host results to [(host, result), ...]."""
    if "results" in result:
        return list(result["results"].items())
    return [(result.get("domain", default_host), result)]


def _add_unique(items: list, new_items) -> None:
    for item in new_items:
        if item not in items:
            items.append(item)


def update_state(state: dict, tool: str, result: dict, target: str) -> dict:
    """Merge one step's result into `state`. Out-of-scope hosts are dropped."""
    for host, res in _per_host(result, target):
        if not res.get("success"):
            continue
        if tool in SUBDOMAIN_TOOLS:
            subs = [s.strip().lower().rstrip(".") for s in res.get("subdomains", [])]
            _add_unique(state["subdomains"], [s for s in subs if in_scope(s, target)])
        elif tool == "curl":
            if res.get("status") and in_scope(host, target):
                _add_unique(state["live_hosts"], [host])
        elif tool == "nikto":
            _add_unique(state["findings"], [
                {"host": host, "id": v.get("id"), "description": v.get("description"), "uri": v.get("uri")}
                for v in res.get("vulnerabilities", [])
            ])
    return state


def summarise(data, max_items: int = 15, max_chars: int = 3000) -> str:
    """Compact JSON for the model: long lists and strings cut down."""
    def trim(value):
        if isinstance(value, dict):
            return {k: trim(v) for k, v in value.items() if k != "raw_output"}
        if isinstance(value, list):
            head = [trim(v) for v in value[:max_items]]
            if len(value) > max_items:
                head.append(f"... {len(value) - max_items} more")
            return head
        if isinstance(value, str) and len(value) > 300:
            return value[:300] + "..."
        return value

    text = json.dumps(trim(data), indent=1)
    return text if len(text) <= max_chars else text[:max_chars] + "\n... (truncated)"
