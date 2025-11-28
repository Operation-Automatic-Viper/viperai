# src/viperai/tools/nikto.py
from .base import ToolExecutor
import xml.etree.ElementTree as ET
from pathlib import Path

class NiktoTool(ToolExecutor):
    binary = "nikto"

    def _build_command(self, domain: str, output_path: str) -> list:
        return [
            "nikto", "-host", f"https://{domain}",
            "-output", output_path,
            "-Format", "xml"
        ]

    def _parse_output(self, raw: str, file_path: str) -> dict:
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            vulns = []
            for item in root.findall(".//item"):
                desc = item.find("description")
                osvdb = item.find("osvdb")
                vulns.append({
                    "id": item.find("id").text,
                    "description": desc.text if desc is not None else "",
                    "osvdb": osvdb.text if osvdb is not None else None
                })
            return {
                "vulnerabilities": vulns,
                "count": len(vulns)
            }
        except Exception as e:
            return {"vulnerabilities": [], "count": 0, "error": str(e)}