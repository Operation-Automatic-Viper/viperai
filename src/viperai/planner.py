# src/viperai/planner.py
import json
import os
import sys
from pathlib import Path

from viperai.settings import load_config, load_tools, tool_names
from viperai.state import summarise

# A step's "input" says where it gets its hosts from (see executor.INPUTS).
VALID_INPUTS = ("target", "subdomains", "live_hosts")


def gemini_llm(model_name):
    """Return a callable (prompt) -> raw text, backed by Gemini. Needs GEMINI_API_KEY."""
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[Error] GEMINI_API_KEY not set. Run: export GEMINI_API_KEY=your-key")
        sys.exit(1)
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    def call(prompt: str) -> str:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1,
                max_output_tokens=8192,
            ),
        )
        raw = response.text
        if isinstance(raw, list):
            raw = "".join(raw)
        return raw if isinstance(raw, str) else str(raw)

    return call


class Planner:
    def __init__(self, target, llm=None, existing_plan=None, config=None, config_dir=None):
        self.target = target
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent / "config"
        self.config = config or load_config(self.config_dir)
        self.tools = load_tools(self.config_dir)
        self.valid_tools = tool_names(self.tools)
        self.llm = llm if llm is not None else gemini_llm(self.config["model"])

        self.base_dir = Path(__file__).parent
        self.sessions_dir = self.base_dir / "sessions"
        self._last_reflection_sig = None

        if existing_plan:
            self.plan = existing_plan
            self.plan["target"] = target
            self.plan.setdefault("session_id", "temp")
            self.plan["steps"] = self._validate_steps(self.plan.get("steps", []))
        else:
            self.plan = self._generate_plan()

        self.plan_file = self.sessions_dir / f"viperai_plan_{self.plan.get('session_id', 'temp')}.json"
        self._save_plan()

    # ---- plan validation -------------------------------------------------

    def _validate_steps(self, steps, start_id=1):
        """Keep only well-formed steps with a known tool and input; renumber ids."""
        clean = []
        for step in steps:
            if not isinstance(step, dict):
                continue
            tool = step.get("chosen_tool")
            if tool not in self.valid_tools:
                continue
            source = step.get("input", "target")
            if source not in VALID_INPUTS:
                source = "target"
            clean.append({
                "id": start_id + len(clean),
                "action": str(step.get("action", ""))[:200],
                "chosen_tool": tool,
                "input": source,
                "status": step.get("status", "pending"),
            })
            if len(clean) >= self.config["max_steps"]:
                break
        return clean

    def _parse_json(self, raw):
        raw = (raw or "").strip()
        if not raw:
            raise ValueError("Empty response from model")
        # Tolerate light truncation of the JSON tail.
        if raw.count("{") > raw.count("}"):
            raw += "}" * (raw.count("{") - raw.count("}"))
        if raw.count("[") > raw.count("]"):
            raw += "]" * (raw.count("[") - raw.count("]"))
        return json.loads(raw)

    # ---- initial plan ----------------------------------------------------

    def _plan_prompt(self):
        return f"""You are ViperAI, an autonomous penetration-testing agent.
Goal: find outdated or vulnerable software on the authorised target {self.target}.
Available tools by category: {json.dumps(self.tools, indent=2)}

Each step runs ONE tool. "input" says which hosts the step runs against:
- "target": the target domain itself
- "subdomains": subdomains discovered by an earlier subdomain-enumeration step
- "live_hosts": hosts an earlier curl step confirmed are live

A sensible flow is: enumerate subdomains, curl them to find live hosts, then scan the
live hosts for vulnerabilities. Only use tool names from the list, and only these inputs.

Return ONLY a JSON object:
{{"steps": [{{"id": 1, "action": "short description", "chosen_tool": "<tool>", "input": "target"}}]}}"""

    def _generate_plan(self):
        try:
            plan = self._parse_json(self.llm(self._plan_prompt()))
            steps = self._validate_steps(plan.get("steps", []))
            if not steps:
                raise ValueError("Model returned no usable steps")
        except SystemExit:
            raise
        except Exception as e:
            print(f"[Error] Could not build a plan from the model: {type(e).__name__}: {e}")
            sys.exit(1)
        return {"target": self.target, "session_id": "temp", "steps": steps}

    # ---- reflection (Sprint 2) ------------------------------------------

    def _reflect_prompt(self, state, remaining):
        remaining_summary = summarise(
            [{"action": s["action"], "chosen_tool": s["chosen_tool"], "input": s["input"]} for s in remaining]
        )
        return f"""You are ViperAI, revising a penetration-testing plan for the authorised target {self.target}.
What has been found so far:
{summarise(state)}

Remaining planned steps:
{remaining_summary}

Available tools by category: {json.dumps(self.tools, indent=2)}
Valid "input" values: target, subdomains, live_hosts.

Revise ONLY the remaining steps so they use what has been found: e.g. once subdomains exist,
curl them (input "subdomains"); once live hosts exist, scan them (input "live_hosts").
Do not plan work on anything outside {self.target} and its subdomains. Keep it focused.

Return ONLY a JSON object: {{"steps": [{{"action": "...", "chosen_tool": "<tool>", "input": "..."}}]}}"""

    def reflect(self, state):
        """After a step, let the model rewrite the remaining (pending) steps from `state`.

        Reflection runs only when the agent has discovered something new since the last
        reflection, which keeps it from re-planning in a loop and avoids wasted model calls.
        On any problem the existing plan is kept, so reflection can only refine, not break.
        """
        # Only react when the findings actually changed (new subdomains/live hosts/findings).
        sig = (len(state["subdomains"]), len(state["live_hosts"]), len(state["findings"]))
        if sig == self._last_reflection_sig:
            return
        self._last_reflection_sig = sig

        done = [s for s in self.plan["steps"] if s["status"] != "pending"]
        remaining = [s for s in self.plan["steps"] if s["status"] == "pending"]
        budget = self.config["max_steps"] - len(done)
        if budget <= 0:
            self.plan["steps"] = done
            self._save_plan()
            return

        try:
            revised = self._parse_json(self.llm(self._reflect_prompt(state, remaining)))
            steps = self._validate_steps(revised.get("steps", []), start_id=len(done) + 1)
            # Drop steps that repeat work already completed (same tool + input).
            done_sigs = {(s["chosen_tool"], s["input"]) for s in done}
            steps = [s for s in steps if (s["chosen_tool"], s["input"]) not in done_sigs]
            steps = steps[:budget]
            for i, s in enumerate(steps):
                s["id"] = len(done) + 1 + i
            if steps:
                self.plan["steps"] = done + steps
                print(f"[Reflection] Revised remaining steps ({len(steps)} planned).")
            else:
                print("[Reflection] No usable revision; keeping the current plan.")
        except Exception as e:
            # Reflection is best-effort: a bad model reply must never break the run.
            print(f"[Reflection] Skipped ({type(e).__name__}); keeping the current plan.")
        self._save_plan()

    # ---- plan bookkeeping ------------------------------------------------

    def _save_plan(self):
        self.plan_file.parent.mkdir(exist_ok=True)
        self.plan_file.write_text(json.dumps(self.plan, indent=2))

    def get_next_step(self):
        for step in self.plan["steps"]:
            if step["status"] == "pending":
                return step
        return None

    def update_step_status(self, step_id, status):
        for step in self.plan["steps"]:
            if step["id"] == step_id:
                step["status"] = status
        self._save_plan()
