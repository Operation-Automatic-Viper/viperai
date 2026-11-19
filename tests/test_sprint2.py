"""Sprint 2 tests: scope filtering, state chaining, executor fan-out, reflection.

All offline: a fake LLM and fake tools stand in for Gemini and the real binaries.
"""
import json

from viperai.scope import in_scope
from viperai.state import new_state, update_state
from viperai.executor import Executor
from viperai.planner import Planner


# ---- scope -----------------------------------------------------------------

def test_in_scope_accepts_target_and_subdomains():
    assert in_scope("example.com", "example.com")
    assert in_scope("www.example.com", "example.com")
    assert in_scope("a.b.example.com", "example.com")


def test_in_scope_rejects_outside_and_lookalikes():
    assert not in_scope("evil.com", "example.com")
    assert not in_scope("notexample.com", "example.com")      # suffix but not a subdomain
    assert not in_scope("example.com.evil.com", "example.com")
    assert not in_scope("example.com; rm -rf /", "example.com")


# ---- state -----------------------------------------------------------------

def test_update_state_collects_in_scope_subdomains_only():
    state = new_state()
    result = {"success": True, "subdomains": ["www.example.com", "evil.com", "WWW.EXAMPLE.COM"]}
    update_state(state, "chaos", result, "example.com")
    assert state["subdomains"] == ["www.example.com"]  # deduped, lowercased, evil.com dropped


def test_update_state_tracks_live_hosts_and_findings():
    state = new_state()
    update_state(state, "curl",
                 {"results": {"www.example.com": {"success": True, "status": "200"},
                              "dead.example.com": {"success": True, "status": None}}},
                 "example.com")
    assert state["live_hosts"] == ["www.example.com"]

    update_state(state, "nikto",
                 {"results": {"www.example.com": {"success": True,
                              "vulnerabilities": [{"id": "1", "description": "x", "uri": "/"}]}}},
                 "example.com")
    assert state["findings"][0]["host"] == "www.example.com"


# ---- executor fan-out ------------------------------------------------------

class RecordingTool:
    def __init__(self):
        self.calls = []

    def run(self, host):
        self.calls.append(host)
        return {"success": True, "domain": host, "status": "200"}


def test_executor_runs_on_target_by_default():
    tool = RecordingTool()
    ex = Executor(tools={"curl": tool})
    ex.run({"chosen_tool": "curl", "input": "target"}, "example.com", new_state())
    assert tool.calls == ["example.com"]


def test_executor_fans_out_over_discovered_hosts_capped_and_in_scope():
    tool = RecordingTool()
    ex = Executor(max_hosts_per_step=2, tools={"curl": tool})
    state = {"subdomains": ["a.example.com", "b.example.com", "c.example.com", "evil.com"],
             "live_hosts": [], "findings": []}
    result = ex.run({"chosen_tool": "curl", "input": "subdomains"}, "example.com", state)
    assert tool.calls == ["a.example.com", "b.example.com"]   # capped at 2, evil.com never reached
    assert result["hosts"] == 2


def test_executor_falls_back_to_target_when_no_hosts_yet():
    tool = RecordingTool()
    ex = Executor(tools={"curl": tool})
    ex.run({"chosen_tool": "curl", "input": "live_hosts"}, "example.com", new_state())
    assert tool.calls == ["example.com"]


# ---- planner: validation and reflection ------------------------------------

def make_planner(target, llm, tmp_path, config=None):
    cfg = {"model": "x", "max_steps": 12, "max_hosts_per_step": 10}
    if config:
        cfg.update(config)
    p = Planner(target, llm=llm, config=cfg)
    p.sessions_dir = tmp_path
    p.plan_file = tmp_path / "plan.json"
    return p


def test_plan_validation_drops_unknown_tools_and_bad_inputs(tmp_path):
    llm = lambda _: json.dumps({"steps": [
        {"action": "enum", "chosen_tool": "chaos", "input": "target"},
        {"action": "bad tool", "chosen_tool": "metasploit", "input": "target"},   # dropped
        {"action": "bad input", "chosen_tool": "curl", "input": "the internet"},  # input -> target
    ]})
    p = make_planner("example.com", llm, tmp_path)
    tools = [s["chosen_tool"] for s in p.plan["steps"]]
    assert tools == ["chaos", "curl"]
    assert p.plan["steps"][1]["input"] == "target"
    assert [s["id"] for s in p.plan["steps"]] == [1, 2]


def test_reflection_rewrites_remaining_steps_from_state(tmp_path):
    plan_llm = lambda _: json.dumps({"steps": [
        {"action": "enum", "chosen_tool": "chaos", "input": "target"},
        {"action": "scan target", "chosen_tool": "nikto", "input": "target"},
    ]})
    p = make_planner("example.com", plan_llm, tmp_path)
    p.update_step_status(1, "completed")  # first step done

    # After finding subdomains, reflection should curl them then scan live hosts.
    p.llm = lambda _: json.dumps({"steps": [
        {"action": "check live", "chosen_tool": "curl", "input": "subdomains"},
        {"action": "scan live", "chosen_tool": "nikto", "input": "live_hosts"},
    ]})
    p.reflect({"subdomains": ["www.example.com"], "live_hosts": [], "findings": []})

    statuses = [(s["chosen_tool"], s["input"], s["status"]) for s in p.plan["steps"]]
    assert statuses[0] == ("chaos", "target", "completed")       # done step preserved
    assert ("curl", "subdomains", "pending") in statuses
    assert ("nikto", "live_hosts", "pending") in statuses


def test_reflection_keeps_plan_when_model_output_is_garbage(tmp_path):
    plan_llm = lambda _: json.dumps({"steps": [
        {"action": "enum", "chosen_tool": "chaos", "input": "target"},
        {"action": "scan", "chosen_tool": "nikto", "input": "target"},
    ]})
    p = make_planner("example.com", plan_llm, tmp_path)
    before = json.dumps(p.plan["steps"])
    p.llm = lambda _: "not json at all {["
    p.reflect(new_state())
    assert json.dumps(p.plan["steps"]) == before  # unchanged


def test_reflection_respects_max_steps_budget(tmp_path):
    plan_llm = lambda _: json.dumps({"steps": [{"action": "enum", "chosen_tool": "chaos", "input": "target"}]})
    p = make_planner("example.com", plan_llm, tmp_path, config={"max_steps": 3})
    p.update_step_status(1, "completed")
    # Model tries to add 10 steps; only 2 fit the budget of 3 total.
    p.llm = lambda _: json.dumps({"steps": [
        {"action": f"s{i}", "chosen_tool": "curl", "input": "subdomains"} for i in range(10)
    ]})
    p.reflect({"subdomains": ["www.example.com"], "live_hosts": [], "findings": []})
    assert len(p.plan["steps"]) == 3
