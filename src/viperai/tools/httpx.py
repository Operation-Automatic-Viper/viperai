# src/viperai/tools/httpx.py
import re
from .base import ToolExecutor


class HttpxTool(ToolExecutor):
    """Live-host probing with ProjectDiscovery httpx (the prober sublistah used to chain)."""
    binary = "httpx"

    def _build_command(self, domain: str, output_path: str) -> list:
        return ["httpx", "-u", domain, "-silent", "-status-code", "-no-color"]

    def _parse_output(self, raw: str, file_path: str) -> dict:
        lines = [l for l in raw.strip().splitlines() if l.strip()]
        line = lines[0] if lines else ""
        m = re.search(r"\[(\d{3})\]", line)
        url = line.split()[0] if line else None
        scheme = url.split("://", 1)[0] if url and "://" in url else None
        return {
            "status": m.group(1) if m else None,
            "url": url,
            "scheme": scheme,
        }
