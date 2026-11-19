# src/viperai/reporter.py
import json
import sys
from pathlib import Path
from datetime import datetime

class Reporter:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.session = None
        self.session_file = None
        self.plan_file = None

    def start_session(self, target, plan):
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session = {
            "session_id": session_id,
            "target": target,
            "start_time": datetime.now().isoformat(),
            "steps": []
        }
        self.session_file = self.base_dir / "sessions" / f"viperai_session_{session_id}.json"
        self.plan_file = self.base_dir / "sessions" / f"viperai_plan_{session_id}.json"
        self._save_plan(plan)
        self.save()

    def _save_plan(self, plan):
        self.plan_file.parent.mkdir(exist_ok=True)
        self.plan_file.write_text(json.dumps(plan, indent=2))

    def log_step(self, step, result):
        self.session["steps"].append({
            "step_id": step["id"],
            "action": step["action"],
            "tool": step.get("chosen_tool"),
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        self.save()

    def save(self):
        if self.session_file:
            self.session_file.write_text(json.dumps(self.session, indent=2))

    def load_session(self, session_path):
        path = Path(session_path)
        if not path.exists():
            print(f"[Error] Session file not found: {path}")
            sys.exit(1)
        self.session = json.loads(path.read_text())
        self.session_file = path
        self.plan_file = self.base_dir / "sessions" / f"viperai_plan_{self.session['session_id']}.json"
        if not self.plan_file.exists():
            print(f"[Error] Plan file not found: {self.plan_file}")
            sys.exit(1)