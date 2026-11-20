# src/viperai/tools/base.py
import re
import subprocess
from pathlib import Path
from typing import Dict, Any
import json

class ToolExecutor:
    binary: str = None           # Must be set in subclass
    timeout: int = 9000           # Seconds
    output_dir: Path = None

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.output_dir = self.base_dir / "output"
        self.output_dir.mkdir(exist_ok=True)

    def run(self, domain: str) -> Dict[str, Any]:
        if not domain:
            return {"success": False, "error": "No domain provided"}

        if not self._check_binary():
            return {"success": False, "error": f"{self.binary} not in PATH"}

        safe = re.sub(r"[^A-Za-z0-9._-]", "_", domain)
        output_file = self.output_dir / f"{self.binary}_{safe}.txt"
        cmd = self._build_command(domain, str(output_file))

        try:
            raw = self._run_command(cmd)
            parsed = self._parse_output(raw, str(output_file))
            return {
                # A parser that set an "error" (e.g. missing output file) is a failure,
                # not a 0-result success.
                "success": "error" not in parsed,
                "tool": self.binary,
                "domain": domain,
                "raw_file": str(output_file),
                **parsed
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Timeout after {self.timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_binary(self) -> bool:
        return subprocess.run(["which", self.binary], capture_output=True).returncode == 0

    def _build_command(self, domain: str, output_path: str) -> list:
        raise NotImplementedError

    def _run_command(self, cmd: list) -> str:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
        return result.stdout + result.stderr

    def _parse_output(self, raw: str, file_path: str) -> Dict[str, Any]:
        raise NotImplementedError