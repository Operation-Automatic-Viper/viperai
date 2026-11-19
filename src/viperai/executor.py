# src/viperai/executor.py
from viperai.tools.chaos import ChaosTool
from viperai.tools.nikto import NiktoTool
from viperai.tools.curl import CurlTool
from viperai.tools.sublistah import SublistahTool

class Executor:
    def __init__(self):
        self.tools = {
            "chaos": ChaosTool(),
            "curl": CurlTool(),
            "nikto": NiktoTool(),
            "sublistah": SublistahTool(),
        }

    def run(self, step, target):
        """Run the step's chosen tool against the scan target."""
        tool_name = step.get("chosen_tool")
        domain = target

        if not tool_name or not domain:
            return {"success": False, "error": "Missing tool or domain"}

        if tool_name not in self.tools:
            return {"success": False, "error": f"Tool '{tool_name}' not available"}

        return self.tools[tool_name].run(domain)