# src/viperai/tools/nikto.py
import xml.etree.ElementTree as ET
from .base import ToolExecutor


class NiktoTool(ToolExecutor):
    binary = "nikto"

    @staticmethod
    def _xml_path(path: str) -> str:
        """nikto -Format xml writes to a .xml file; keep write and read paths in sync."""
        if path.endswith(".xml"):
            return path
        if path.endswith(".txt"):
            return path[:-4] + ".xml"
        return path + ".xml"

    def _build_command(self, domain: str, output_path: str) -> list:
        # `domain` may already carry the scheme the prober found; only default it if not.
        host = domain if "://" in domain else f"https://{domain}"
        return [
            "nikto", "-host", host,
            "-output", self._xml_path(output_path),
            "-Format", "xml",
        ]

    def _parse_output(self, raw: str, file_path: str) -> dict:
        try:
            tree = ET.parse(self._xml_path(file_path))
            root = tree.getroot()
            vulns = []
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
            return {"vulnerabilities": vulns, "count": len(vulns)}
        except Exception as e:
            return {"vulnerabilities": [], "count": 0, "error": str(e)}
