# src/viperai/tools/curl.py
from .base import ToolExecutor

class CurlTool(ToolExecutor):
    binary = "curl"

    def _build_command(self, domain: str, output_path: str) -> list:
        return [
            "curl", "-I", "-L", "--max-time", "10",
            "--silent", "--show-error",
            f"https://{domain}"
        ]

    def _parse_output(self, raw: str, file_path: str) -> dict:
        headers = {}
        lines = raw.strip().splitlines()
        status_line = lines[0] if lines else ""
        if "HTTP/" in status_line:
            parts = status_line.split(" ", 2)
            headers["status"] = parts[1] if len(parts) > 1 else "Unknown"

        for line in lines[1:]:
            if ": " in line:
                k, v = line.split(": ", 1)
                headers[k.lower()] = v

        return {
            "status": headers.get("status"),
            "server": headers.get("server"),
            "headers": headers
        }