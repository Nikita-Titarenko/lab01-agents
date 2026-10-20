import pytest

from agent.errors import DecisionError
from agent.state import Decision
from agent.validator import validate_decision


def test_validator_rejects_unknown_action() -> None:
    with pytest.raises(DecisionError):
        validate_decision(
            Decision(
                action="drop_cache_cluster",
                arguments={},
                decision_summary="Invalid action",
            )
        )


def test_validator_requires_strategy_name_for_tradeoffs() -> None:
    with pytest.raises(DecisionError):
        validate_decision(
            Decision(
                action="get_implementations",
                arguments={"strategy_name": "   "},
                decision_summary="Need tradeoff details",
            )
        )


def test_validator_requires_language_for_tradeoffs() -> None:
    with pytest.raises(DecisionError):
        validate_decision(
            Decision(
                action="get_implementations",
                arguments={"strategy_name": "cache_aside", "language": "   "},
                decision_summary="Need language-specific tradeoff details",
            )
        )