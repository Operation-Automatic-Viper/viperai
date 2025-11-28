# src/viperai/tools/chaos.py
from .base import ToolExecutor
from pathlib import Path

class ChaosTool(ToolExecutor):
    binary = "chaos"
    def _build_command(self, domain: str, output_path: str) -> list:
        print("DOMAIN = "+domain)
        return ["chaos", "-d", domain, "-o", output_path]

    def _parse_output(self, raw: str, file_path: str) -> dict:
        try:
            lines = Path(file_path).read_text().splitlines()
            subs = [line.strip() for line in lines if line.strip() and "." in line]
            return {
                "subdomains": subs,
                "count": len(subs)
            }
        except Exception as e:
            return {"subdomains": [], "count": 0, "error": str(e)}