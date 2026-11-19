<div align="center">
  <img src="images/logo.png" alt="ViperAI logo" width="80" height="80">
  <h1>ViperAI</h1>
  <p>A prototype LLM agent that plans and runs reconnaissance and scanning tools for penetration testing.</p>
</div>

> **Status: early prototype (Sprint 1 of 5).** The planning loop, tool adapters and session
> resume work. Reflection, CVE lookup and reporting are planned; see [Roadmap](#roadmap).

> **Use only on targets you own or have written permission to test.** ViperAI asks you to
> confirm authorisation before every scan. Good practice targets: your own lab,
> [`scanme.nmap.org`](http://scanme.nmap.org/) (explicitly allows scanning), or deliberately
> vulnerable apps such as DVWA or Hack The Box machines.

## How it works

```
target ──► Planner (Gemini) ──► plan: ordered steps, each with a chosen tool
                                   │
              ┌────────────────────┘
              ▼
          Executor ──► tool adapters (chaos, sublistah, curl, nikto) via subprocess
              │
              ▼
          Reporter ──► session JSON (saved after every step, resumable)
```

1. **Planner** (`planner.py`) sends the goal ("find outdated or vulnerable software on the
   target") and the tool catalogue (`config/tools.json`) to Gemini, which returns a JSON plan.
2. **Executor** (`executor.py`) runs each step's chosen tool against the target. Each adapter in
   `tools/` builds the command and parses the output into structured data.
3. **Reporter** (`reporter.py`) logs every step and result to a session file, so an interrupted
   run (Ctrl+C) can be resumed.

Commands are run as argument lists (no shell), and the target must be a plain hostname.

## Getting started

### Prerequisites

- Python 3.11+ and [Poetry](https://python-poetry.org)
- A Gemini API key, set as `GEMINI_API_KEY`
- The tools you want the agent to use, on your `PATH`:
  - [`chaos`](https://github.com/projectdiscovery/chaos-client) (needs a ProjectDiscovery API key, `PDCP_API_KEY`)
  - [`nikto`](https://github.com/sullo/nikto)
  - `curl`
  - `sublistah.sh`: a custom subdomain enumeration script (not yet included in this repo)

Missing tools are reported as errors for that step; the run continues.

### Install

```sh
git clone https://github.com/Operation-Automatic-Viper/viperai.git
cd viperai
poetry install
export GEMINI_API_KEY='your-key'
```

The Gemini model is set in `src/viperai/config/viperai.yaml` (default `gemini-2.5-flash`).

## Usage

```sh
# Plan and run a scan (asks you to confirm authorisation first)
poetry run viperai scan scanme.nmap.org

# Skip the prompt once you have confirmed authorisation, e.g. in scripts
poetry run viperai scan scanme.nmap.org --yes

# Resume an interrupted run
poetry run viperai resume src/viperai/sessions/viperai_session_<id>.json
```

Sessions and raw tool output are written to `src/viperai/sessions/` and `src/viperai/output/`
(both git-ignored).

## Tests

```sh
pip install pytest
PYTHONPATH=src python -m pytest
```

The tests cover target validation, the authorisation check and the tool output parsers. They
need no API key and no network access.

## Roadmap

- [x] **Sprint 1:** LLM planning, tool adapters (chaos, sublistah, curl, nikto), session resume
- [ ] **Sprint 2:** Reflection loop (revise remaining steps from each result) and chaining outputs between steps, e.g. scanning each discovered subdomain
- [ ] **Sprint 3:** Fingerprinting from more sources (Wappalyzer, TLS, crt.sh)
- [ ] **Sprint 4:** CVE lookup, risk scoring, approval gate before intrusive steps
- [ ] **Sprint 5:** PDF reporting, fuller test suite

**Known issue:** the planner uses the `google-generativeai` SDK, which Google has deprecated;
migrating to `google-genai` is planned.

## Authors

- Rayen Guedria ([rayenguedria.github.io](https://rayenguedria.github.io))
- Oussama

## License

MIT, see [LICENSE](LICENSE).
