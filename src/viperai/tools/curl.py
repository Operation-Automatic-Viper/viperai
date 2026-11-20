# src/viperai/tools/curl.py
import subprocess
from .base import ToolExecutor


class CurlTool(ToolExecutor):
    """HTTP(S) prober: tries https then http so http-only hosts are not missed."""
    binary = "curl"

    def _build_command(self, url: str, output_path: str) -> list:
        return [
            "curl", "-I", "-L", "--max-time", "10",
            "--silent", "--show-error",
            url,
        ]

    def run(self, domain: str) -> dict:
        if not domain:
            return {"success": False, "error": "No domain provided"}
        if not self._check_binary():
            return {"success": False, "error": f"{self.binary} not in PATH"}

        # If a scheme was already supplied, honour it; otherwise probe https then http.
        schemes = [domain.split("://", 1)[0]] if "://" in domain else ["https", "http"]
        host = domain.split("://", 1)[-1]
        last_error = None
        for scheme in schemes:
            url = f"{scheme}://{host}"
            try:
                parsed = self._parse_output(self._run_command(self._build_command(url, "")), "")
            except subprocess.TimeoutExpired:
                last_error = f"Timeout after {self.timeout}s"
                continue
            except Exception as e:
                last_error = str(e)
                continue
            if parsed.get("status"):
                parsed["scheme"] = scheme
                return {"success": True, "tool": "curl", "domain": host, **parsed}
        return {"success": False, "tool": "curl", "domain": host,
                "error": last_error or "no response on https/http"}

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
            "headers": headers,
        }
