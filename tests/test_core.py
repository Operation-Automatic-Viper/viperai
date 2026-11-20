"""Offline tests: no API key, no network, no external tools needed."""
from viperai.scope import is_valid_target, confirm_authorised
from viperai.tools.curl import CurlTool
from viperai.tools.nikto import NiktoTool
from viperai.tools.amass import AmassTool
from viperai.tools.httpx import HttpxTool


def test_valid_hostnames():
    for target in ["example.com", "scanme.nmap.org", "sub.example.co.uk", "a-b.example.com"]:
        assert is_valid_target(target), target


def test_rejects_urls_paths_and_injection():
    for target in [
        "", "localhost", "https://example.com", "example.com/admin", "example.com:8080",
        "-oX.example.com", "example.com; rm -rf /", "../etc/passwd", "exa mple.com",
    ]:
        assert not is_valid_target(target), target


def test_authorisation_requires_explicit_yes():
    assert confirm_authorised("example.com", ask=lambda _: "yes")
    assert confirm_authorised("example.com", ask=lambda _: "  YES ")
    assert not confirm_authorised("example.com", ask=lambda _: "y")
    assert not confirm_authorised("example.com", ask=lambda _: "")


def test_assume_yes_skips_prompt():
    def never_called(_):
        raise AssertionError("prompt should not be shown")
    assert confirm_authorised("example.com", assume_yes=True, ask=never_called)


def test_curl_parses_status_and_headers():
    raw = "HTTP/2 200\r\nServer: nginx/1.18.0\r\nX-Powered-By: PHP/7.4\r\n"
    parsed = CurlTool()._parse_output(raw, "")
    assert parsed["status"] == "200"
    assert parsed["server"] == "nginx/1.18.0"
    assert parsed["headers"]["x-powered-by"] == "PHP/7.4"


def test_nikto_parses_xml(tmp_path):
    xml = tmp_path / "nikto.xml"
    # Same shape as Nikto's -Format xml output: id/osvdbid/method are attributes.
    xml.write_text(
        "<niktoscan><scandetails targetip='192.0.2.1' targethostname='example.com'>"
        "<item id='999986' osvdbid='3233' method='GET'>"
        "<description><![CDATA[Server leaks inodes via ETags]]></description><uri><![CDATA[/]]></uri></item>"
        "<item id='999100' osvdbid='0' method='GET'>"
        "<description><![CDATA[Uncommon header 'x-powered-by' found]]></description><uri><![CDATA[/]]></uri></item>"
        "</scandetails></niktoscan>"
    )
    parsed = NiktoTool()._parse_output("", str(xml))
    assert "error" not in parsed
    assert parsed["count"] == 2
    first, second = parsed["vulnerabilities"]
    assert first["id"] == "999986" and first["osvdb"] == "3233" and first["uri"] == "/"
    assert second["osvdb"] is None
    assert second["description"].startswith("Uncommon header")


def test_amass_parses_subdomains_from_file(tmp_path):
    out = tmp_path / "amass.txt"
    out.write_text("www.example.com\nmail.example.com\nnot a host line\n")
    tool = AmassTool()
    assert tool.binary == "amass"
    assert tool._build_command("example.com", str(out))[:2] == ["amass", "enum"]
    parsed = tool._parse_output("", str(out))
    assert parsed["subdomains"] == ["www.example.com", "mail.example.com"]
    assert parsed["count"] == 2


def test_httpx_parses_status_and_url():
    tool = HttpxTool()
    assert tool.binary == "httpx"
    assert tool._build_command("example.com", "")[:2] == ["httpx", "-u"]
    parsed = tool._parse_output("https://example.com [200]\n", "")
    assert parsed["status"] == "200"
    assert parsed["url"] == "https://example.com"
    assert tool._parse_output("", "")["status"] is None
