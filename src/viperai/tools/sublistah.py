# src/viperai/tools/sublistah.py
from .base import ToolExecutor

class SublistahTool(ToolExecutor):
    binary = "sublistahh.sh"   # ← your tool name

    def _build_command(self, domain: str, output_path: str) -> list:
        # sublistah.sh usually outputs to stdout
        return ["sublistah.sh", domain]

    def _parse_output(self, raw: str, file_path: str) -> dict:
        lines = [line.strip() for line in raw.splitlines() if line.strip() and not line.startswith("#")]
        subdomains = [line.split()[0] if " " in line else line for line in lines]
        return {
            "subdomains": subdomains,
            "count": len(subdomains),
            "raw_output": raw.strip()
        }