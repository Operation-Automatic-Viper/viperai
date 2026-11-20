# src/viperai/tools/amass.py
from .base import ToolExecutor
from pathlib import Path


class AmassTool(ToolExecutor):
    """Passive subdomain enumeration with OWASP amass."""
    binary = "amass"

    def _build_command(self, domain: str, output_path: str) -> list:
        # Passive only: no active brute/resolution against the target.
        return ["amass", "enum", "-passive", "-d", domain, "-nocolor", "-o", output_path]

    def _parse_output(self, raw: str, file_path: str) -> dict:
        try:
            lines = Path(file_path).read_text().splitlines()
            subs = [l.strip() for l in lines if l.strip() and "." in l and " " not in l.strip()]
            return {"subdomains": subs, "count": len(subs)}
        except Exception as e:
            return {"subdomains": [], "count": 0, "error": str(e)}
