from __future__ import annotations

from agent.errors import DecisionError
from agent.state import Decision

ALLOWED_ACTIONS = {"lookup_caching_strategy", "get_implementations", "finish"}


def _require_non_empty_string(arguments: dict[str, str], key: str, action: str) -> str:
    value = arguments.get(key)
    if not isinstance(value, str) or not value.strip():
        raise DecisionError(f"Action '{action}' requires a non-empty string argument '{key}'.")
    return value.strip()


def validate_decision(decision: Decision) -> Decision:
    if decision.action not in ALLOWED_ACTIONS:
        raise DecisionError(
            f"Unknown action '{decision.action}'. Allowed actions: {sorted(ALLOWED_ACTIONS)}."
        )

    if not isinstance(decision.arguments, dict):
        raise DecisionError("Decision arguments must be a JSON object.")

    if decision.action == "lookup_caching_strategy":
        _require_non_empty_string(decision.arguments, "strategy_name", decision.action)

    if decision.action == "get_implementations":
        _require_non_empty_string(decision.arguments, "strategy_name", decision.action)
        _require_non_empty_string(decision.arguments, "language", decision.action)

    if decision.action == "finish":
        _require_non_empty_string(decision.arguments, "answer", decision.action)
        if not decision.decision_summary.strip():
            raise DecisionError("Action 'finish' requires a non-empty decision summary.")

    return decision