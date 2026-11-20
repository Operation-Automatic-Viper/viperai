<div align="center">
  <img src="images/logo.png" alt="ViperAI logo" width="80" height="80">
  <h1>ViperAI</h1>
  <p>A prototype LLM agent that plans and runs reconnaissance and scanning tools for penetration testing.</p>
</div>

> **Status: prototype (Sprint 2 of 5).** Planning, tool adapters, session resume, a reflection
> loop and output chaining work. CVE lookup and reporting are planned; see [Roadmap](#roadmap).

> **Use only on targets you own or have written permission to test.** ViperAI asks you to
> confirm authorisation before every scan. Good practice targets: your own lab,
> [`scanme.nmap.org`](http://scanme.nmap.org/) (explicitly allows scanning), or deliberately
> vulnerable apps such as DVWA or Hack The Box machines.

## How it works

```
target ──► Planner (Gemini) ──► plan: ordered steps, each with a tool and an input
              ▲                    │
              │ reflect            ▼
              │              Executor ──► tool adapters (amass, chaos, httpx, curl, nikto)
              │                    │
            State ◄────────────────┘   subdomains / live hosts / findings
              │
              ▼
          Reporter ──► session JSON (saved after every step, resumable)
```

1. **Planner** (`planner.py`) asks Gemini for a JSON plan of steps. Each step names one tool and
   an **input**: the `target`, the `subdomains` found so far, or the `live_hosts` found so far.
2. **Executor** (`executor.py`) runs the step's tool against its input hosts.
3. **State** (`state.py`) collects what each step found — subdomains, live hosts, findings.
4. **Reflection:** after each step the planner shows Gemini the state and lets it rewrite the
   *remaining* steps, so results feed the next actions (e.g. curl the subdomains just found,
   then scan the hosts that answered). Reflection can only refine the plan; if the model's
   reply is unusable, the existing plan is kept.
5. **Reporter** (`reporter.py`) logs every step to a session file, so a run interrupted with
   Ctrl+C can be resumed.

**Scope and limits.** Steps only ever run against the authorised target and its subdomains;
any host the model proposes outside that scope is dropped. The number of plan steps
(`max_steps`) and the hosts scanned per step (`max_hosts_per_step`) are capped in
`config/viperai.yaml`. Commands run as argument lists (no shell), and the target must be a
plain hostname.

## Getting started

### Prerequisites

- Python 3.11+ and [Poetry](https://python-poetry.org)
- A Gemini API key, set as `GEMINI_API_KEY`
- The tools you want the agent to use, on your `PATH`:
  - [`amass`](https://github.com/owasp-amass/amass) — passive subdomain enumeration
  - [`chaos`](https://github.com/projectdiscovery/chaos-client) (needs a ProjectDiscovery API key, `PDCP_API_KEY`)
  - [`httpx`](https://github.com/projectdiscovery/httpx) — live-host probing
  - [`nikto`](https://github.com/sullo/nikto) — vulnerability scan. Its XML output needs the Perl
    module `XML::Writer` (`cpan XML::Writer`, or e.g. `pacman -S perl-xml-writer` / `apt install libxml-writer-perl`)
  - `curl`

Missing tools are reported as errors for that step; the run continues.

### Install

```sh
git clone https://github.com/Operation-Automatic-Viper/viperai.git
cd viperai
poetry install
export GEMINI_API_KEY='your-key'
```

The Gemini model is set in `src/viperai/config/viperai.yaml` (default `gemini-3.8-flash`).
On a free-tier key the API rate-limits (a few requests per minute), which can throttle or
interrupt a run; a billed key avoids this.

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

- [x] **Sprint 1:** LLM planning, tool adapters (amass, chaos, httpx, curl, nikto), session resume
- [x] **Sprint 2:** Reflection loop (revise remaining steps from each result) and output chaining — subdomains feed curl, live hosts feed the vulnerability scan — with scope and step/host caps
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
