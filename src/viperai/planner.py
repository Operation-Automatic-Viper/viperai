import json
import os
import sys
from pathlib import Path
import yaml
import google.generativeai as genai

class Planner:
    def __init__(self, target, existing_plan=None):
        # 1. SET base_dir FIRST (before anything uses it)
        self.target = target
        self.base_dir = Path(__file__).parent.parent  # /home/rayen/viperai
        self.config_dir = self.base_dir / "viperai" / "config"  # /home/rayen/viperai/src/viperai/config
        self.tools_file = self.config_dir / "tools.json"
        
        # 2. Now generate or load plan
        if existing_plan:
            self.plan = existing_plan
            self.plan["target"] = self.target
            self.plan["session_id"] = self.plan.get("session_id", "temp")
        else:
            self.plan = self._generate_plan()
        
        # 3. Ensure every step has status
        for step in self.plan.get("steps", []):
            step.setdefault("status", "pending")
        
        # 4. Save plan
        self.plan_file = self.base_dir /"viperai" / "sessions" / f"viperai_plan_{self.plan.get('session_id', 'temp')}.json"
        self._save_plan()

    def _model_name(self, default="gemini-2.5-flash"):
        """Gemini model from config/viperai.yaml, falling back to a default."""
        config_file = self.config_dir / "viperai.yaml"
        if config_file.exists():
            config = yaml.safe_load(config_file.read_text()) or {}
            return config.get("gemini-api", {}).get("model", default)
        return default

    def _generate_plan(self):
        # Load tools.json (using self.tools_file, no hard path)
        if not self.tools_file.exists():
            raise FileNotFoundError(f"tools.json missing at {self.tools_file}")
        tools = json.loads(self.tools_file.read_text())
        
        # Get API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("[Error] GEMINI_API_KEY not set. Run: export GEMINI_API_KEY=your-key")
            sys.exit(1)
        genai.configure(api_key=api_key)
        
        prompt = f'''
You are ViperAI, an autonomous pentester AI.
Goal: Find outdated or vulnerable software on {self.target}
Available tools: {json.dumps(tools, indent=2)}
Only use tool names that appear in the list above; "chosen_tool" must be exactly one of them.
Return a JSON **object** with this **exact structure**:
```json
{{
  "steps": [
    {{
      "id": 1,
      "action": "Short description of what to do",
      "tool_suggestions": ["tool1", "tool2"],
      "chosen_tool": "tool1"
    }},
    {{
      "id": 2,
      "action": "Next step...",
      "tool_suggestions": ["tool3"],
      "chosen_tool": "tool3"
    }}
  ]
}}'''
        try:
            model = genai.GenerativeModel(self._model_name())
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                    max_output_tokens=8192 # INCREASED TO 8K
                )
            )
            # Handle list or string
            raw_text = response.text
            if isinstance(raw_text, list):
                raw_text = ''.join(raw_text)
            elif not isinstance(raw_text, str):
                raw_text = str(raw_text)
            raw_text = raw_text.strip()
            if not raw_text:
                raise ValueError("Empty response from Gemini")
            # Fix common truncation: if ends abruptly, try to close braces
            if raw_text.count('{') > raw_text.count('}'):
                raw_text += ']}' # Assume array of steps
            if raw_text.count('[') > raw_text.count(']'):
                raw_text += ']'
            plan = json.loads(raw_text)
            if not isinstance(plan, dict):
                raise ValueError("Response is not a JSON object")
            # Ensure steps exist
            if "steps" not in plan or not isinstance(plan["steps"], list):
                raise ValueError("Missing or invalid 'steps' in plan")
            plan["target"] = self.target
            plan["session_id"] = "temp"
            plan["steps"] = [{**s, "status": "pending"} for s in plan["steps"]]
            return plan
        except json.JSONDecodeError as e:
            print(f"[Error] Invalid JSON from Gemini: {e}")
            print(f"Raw (first 500 chars): {raw_text[:500]}...")
            sys.exit(1)
        except Exception as e:
            print(f"[Error] Gemini API failed: {e}")
            sys.exit(1)
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
    def reflect(self, result):
        # Planned (Sprint 2): let the model revise the remaining steps based on `result`.
        print("[Reflection] Not implemented yet; continuing with the original plan.")