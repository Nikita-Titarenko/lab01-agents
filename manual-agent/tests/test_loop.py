from pathlib import Path

from agent.loop import run_agent
from agent.state import AgentState, Decision


def test_agent_finishes_when_decision_requests_finish(tmp_path: Path) -> None:
    def scripted_decision(_goal: str, _observations: list[str], _step: int, _max_steps: int) -> Decision:
        return Decision(
            action="finish",
            arguments={"answer": "Done"},
            decision_summary="Enough verified observations are available.",
        )

    state = run_agent("Коротко поясни Cache-Aside", decide_fn=scripted_decision, trace_dir=tmp_path)

    assert state.stop_reason == "finish"
    assert state.final_answer == "Done"
    assert state.step == 1


def test_agent_stops_after_max_steps(tmp_path: Path) -> None:
    def scripted_decision(_goal: str, _observations: list[str], _step: int, _max_steps: int) -> Decision:
        return Decision(
            action="lookup_caching_strategy",
            arguments={"strategy_name": "cache_aside"},
            decision_summary="Need verified facts before finishing.",
        )

    state = run_agent("Не завершуй відповідь", decide_fn=scripted_decision, max_steps=2, trace_dir=tmp_path)

    assert state.stop_reason == "max_steps"
    assert state.step == 2
    assert "step limit" in state.final_answer


def test_unknown_action_becomes_observation(tmp_path: Path) -> None:
    decisions = iter(
        [
            Decision(action="unknown", arguments={}, decision_summary="bad"),
            Decision(
                action="finish",
                arguments={"answer": "Recovered after the error."},
                decision_summary="The error is already visible in the observations.",
            ),
        ]
    )

    def scripted_decision(_goal: str, _observations: list[str], _step: int, _max_steps: int) -> Decision:
        return next(decisions)

    state = run_agent("Перевір валідатор", decide_fn=scripted_decision, trace_dir=tmp_path)

    assert state.stop_reason == "finish"
    assert "Unknown action" in state.observations[0]
    assert state.final_answer == "Recovered after the error."


def test_stops_at_max_llm_calls(tmp_path: Path) -> None:
    def scripted_decision(_goal: str, _observations: list[str], _step: int, _max_steps: int) -> Decision:
        return Decision(
            action="lookup_caching_strategy",
            arguments={"strategy_name": "cache_aside"},
            decision_summary="Need another verified fact.",
        )

    state = run_agent(
        "Keep collecting facts",
        decide_fn=scripted_decision,
        max_steps=5,
        max_llm_calls=2,
        trace_dir=tmp_path,
    )

    assert state.stop_reason == "max_llm_calls"
    assert state.llm_calls == 2
    assert "LLM call limit" in state.final_answer