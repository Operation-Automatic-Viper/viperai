# src/viperai/main.py
import sys
import json
from pathlib import Path
from viperai.planner import Planner
from viperai.reporter import Reporter
from viperai.executor import Executor
def main():
    if len(sys.argv) < 2:
        print("Usage: viperai scan <target> | resume <session.json>")
        sys.exit(1)

    command = sys.argv[1]
    reporter = Reporter()

    if command == "scan":
        target = sys.argv[2]
        print(f"[ViperAI] Starting scan on {target}")
        planner = Planner(target)
        plan = planner.plan
        plan["session_id"] = "temp"
        reporter.start_session(target, plan)
        planner.plan["session_id"] = reporter.session["session_id"]
        planner._save_plan()
        run_loop(planner, reporter)

    elif command == "resume":
        session_file = sys.argv[2]
        print(f"[ViperAI] Resuming from {session_file}")
        reporter.load_session(session_file)
        plan = json.loads(reporter.plan_file.read_text())
        planner = Planner(reporter.session["target"], existing_plan=plan)
        run_loop(planner, reporter)

    else:
        print("Invalid command.")
        sys.exit(1)

# In run_loop()
def run_loop(planner, reporter):
    executor = Executor()
    target = planner.target  # ← GET FROM PLANNER

    try:
        while True:
            step = planner.get_next_step()
            if not step:
                print("[ViperAI] Goal achieved!")
                break

            print(f"[Step {step['id']}] {step['action']} → {step.get('chosen_tool')}")

            # PASS TARGET TO EXECUTOR
            result = executor.run(step, target)  # ← ADD target

            reporter.log_step(step, result)
            planner.update_step_status(step["id"], "completed")
            planner.reflect(result)
            reporter.save()

    except KeyboardInterrupt:
        print("\n[ViperAI] Saving state...")
        reporter.save()
        print(f"Resume with: viperai resume {reporter.session_file}")

if __name__ == "__main__":
    main()