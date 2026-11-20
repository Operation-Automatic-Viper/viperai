# src/viperai/executor.py
from viperai.scope import in_scope
from viperai.tools.amass import AmassTool
from viperai.tools.chaos import ChaosTool
from viperai.tools.nikto import NiktoTool
from viperai.tools.curl import CurlTool
from viperai.tools.httpx import HttpxTool

# Where a step takes its hosts from: the target itself, or what earlier steps found.
INPUTS = ("target", "subdomains", "live_hosts")


class Executor:
    def __init__(self, max_hosts_per_step: int = 10, tools: dict = None):
        self.max_hosts_per_step = max_hosts_per_step
        self.tools = tools if tools is not None else {
            "amass": AmassTool(),
            "chaos": ChaosTool(),
            "httpx": HttpxTool(),
            "curl": CurlTool(),
            "nikto": NiktoTool(),
        }

    def hosts_for(self, step: dict, target: str, state: dict) -> list:
        """Hosts this step should run on, in scope and capped. Falls back to the target."""
        source = step.get("input", "target")
        if source not in INPUTS or source == "target":
            return [target]
        hosts = [h for h in state.get(source, []) if in_scope(h, target)]
        return hosts[: self.max_hosts_per_step] or [target]

    def _tool_target(self, tool_name: str, host: str, state: dict) -> str:
        """nikto needs a URL; point it at the scheme the prober found (default https)."""
        if tool_name == "nikto":
            scheme = (state or {}).get("schemes", {}).get(host, "https")
            return f"{scheme}://{host}"
        return host

    def run(self, step: dict, target: str, state: dict = None) -> dict:
        """Run the step's chosen tool on each of its hosts."""
        tool_name = step.get("chosen_tool")
        if not tool_name or not target:
            return {"success": False, "error": "Missing tool or target"}
        if tool_name not in self.tools:
            return {"success": False, "error": f"Tool '{tool_name}' not available"}

        hosts = self.hosts_for(step, target, state or {})
        tool = self.tools[tool_name]
        if hosts == [target]:
            return tool.run(self._tool_target(tool_name, target, state or {}))

        results = {}
        for host in hosts:
            print(f"    → {tool_name} on {host}")
            results[host] = tool.run(self._tool_target(tool_name, host, state or {}))
        return {
            "success": any(r.get("success") for r in results.values()),
            "tool": tool_name,
            "input": step.get("input"),
            "hosts": len(hosts),
            "results": results,
        }
