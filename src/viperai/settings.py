# src/viperai/settings.py
"""Settings from config/viperai.yaml, with safe defaults for anything missing."""
from pathlib import Path

import yaml

CONFIG_DIR = Path(__file__).parent / "config"

DEFAULTS = {
    "model": "gemini-2.5-flash",
    "max_steps": 12,           # total plan steps, including ones added by reflection
    "max_hosts_per_step": 10,  # cap when a step runs on discovered subdomains / live hosts
}


def load_config(config_dir: Path = CONFIG_DIR) -> dict:
    config = dict(DEFAULTS)
    path = config_dir / "viperai.yaml"
    if path.exists():
        raw = yaml.safe_load(path.read_text()) or {}
        config["model"] = raw.get("gemini-api", {}).get("model", config["model"])
        agent = raw.get("agent", {}) or {}
        for key in ("max_steps", "max_hosts_per_step"):
            if isinstance(agent.get(key), int) and agent[key] > 0:
                config[key] = agent[key]
    return config


def load_tools(config_dir: Path = CONFIG_DIR) -> dict:
    """Tool catalogue shown to the model: {category: [tool names]}."""
    import json
    return json.loads((config_dir / "tools.json").read_text())


def tool_names(tools: dict) -> set:
    return {name for names in tools.values() for name in names}
