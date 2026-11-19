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
            # Nikto XML: <item id="..." osvdbid="..." method="GET"><description/><uri/></item>
            for item in root.findall(".//item"):
                desc = item.find("description")
                uri = item.find("uri")
                osvdb = item.get("osvdbid")
                vulns.append({
                    "id": item.get("id"),
                    "description": (desc.text or "").strip() if desc is not None else "",
                    "uri": (uri.text or "").strip() if uri is not None else None,
                    "method": item.get("method"),
                    "osvdb": osvdb if osvdb not in (None, "", "0") else None,
                })
            return {
                "vulnerabilities": vulns,
                "count": len(vulns)
            }
        except Exception as e:
            return {"vulnerabilities": [], "count": 0, "error": str(e)}