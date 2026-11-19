# src/viperai/scope.py
"""Target validation and authorisation check, run before any tool touches a target."""
import re

# A plain hostname such as example.com or sub.example.co.uk: no scheme, path, port or spaces.
_HOSTNAME = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))+$"
)


def is_valid_target(target: str) -> bool:
    """True if `target` is a bare hostname the tools can safely receive."""
    return bool(target) and bool(_HOSTNAME.match(target))


def in_scope(host: str, target: str) -> bool:
    """True if `host` is the authorised target or one of its subdomains."""
    if not isinstance(host, str):
        return False
    host = host.strip().lower().rstrip(".")
    target = target.strip().lower().rstrip(".")
    return is_valid_target(host) and (host == target or host.endswith("." + target))


def confirm_authorised(target: str, assume_yes: bool = False, ask=input) -> bool:
    """Ask the operator to confirm they are allowed to test `target`.

    Scanning systems you do not own or have written permission to test can be illegal.
    """
    if assume_yes:
        return True
    print(
        f"[ViperAI] About to run reconnaissance and scanning tools against {target}.\n"
        "Only continue if you own this target or have written permission to test it."
    )
    answer = ask("Type 'yes' to confirm you are authorised: ")
    return answer.strip().lower() == "yes"
