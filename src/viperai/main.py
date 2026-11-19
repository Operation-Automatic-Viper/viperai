# src/viperai/main.py
import sys
import json
from pathlib import Path
from viperai.planner import Planner
from viperai.reporter import Reporter
from viperai.executor import Executor
from viperai.scope import is_valid_target, confirm_authorised

USAGE = "Usage: viperai scan <target> [--yes] | resume <session.json>"


def main():
    args = sys.argv[1:]
    assume_yes = "--yes" in args
    args = [a for a in args if a != "--yes"]

    if len(args) < 2:
        print(USAGE)
        sys.exit(1)

    command = args[0]

    if command == "scan":
        target = args[1]
        if not is_valid_target(target):
            print(f"[Error] '{target}' is not a valid hostname (use e.g. example.com, no https:// or path).")
            sys.exit(1)
        if not confirm_authorised(target, assume_yes):
            print("[ViperAI] Aborted: authorisation not confirmed.")
            sys.exit(1)
        reporter = Reporter()
        print(f"[ViperAI] Starting scan on {target}")
        planner = Planner(target)
        plan = planner.plan
        plan["session_id"] = "temp"
        reporter.start_session(target, plan)
        planner.plan["session_id"] = reporter.session["session_id"]
        planner._save_plan()
        run_loop(planner, reporter)

    elif command == "resume":
        session_file = args[1]
        reporter = Reporter()
        print(f"[ViperAI] Resuming from {session_file}")
        reporter.load_session(session_file)
        plan = json.loads(reporter.plan_file.read_text())
        planner = Planner(reporter.session["target"], existing_plan=plan)
        run_loop(planner, reporter)

    else:
        print(USAGE)
        sys.exit(1)


def run_loop(planner, reporter):
    executor = Executor()
    target = planner.target

    try:
        while True:
            step = planner.get_next_step()
            if not step:
                print("[ViperAI] Goal achieved!")
                break

            print(f"[Step {step['id']}] {step['action']} → {step.get('chosen_tool')}")

            result = executor.run(step, target)

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