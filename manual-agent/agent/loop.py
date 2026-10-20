from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable
from uuid import uuid4

from agent.environment import NOT_FOUND, get_implementations, lookup_caching_strategy
from agent.errors import DecisionError
from agent.reasoning import decide_with_gemini
from agent.state import AgentState, Decision
from agent.validator import validate_decision

MAX_STEPS = 7
MAX_LLM_CALLS = 7
DecisionFunction = Callable[[str, list[str], int, int], Decision]


def dispatch_action(state: AgentState, decision: Decision) -> str:
    if decision.action == "finish":
        state.final_answer = decision.arguments["answer"]
        state.stop_reason = "finish"
        state.finished = True
        return f"Goal finished: {state.final_answer}"

    if decision.action == "lookup_caching_strategy":
        strategy_name = decision.arguments["strategy_name"]
        result = lookup_caching_strategy(strategy_name)
        if result == NOT_FOUND:
            return f"lookup_caching_strategy('{strategy_name}') -> {NOT_FOUND}"
        formatted_result = json.dumps(result, ensure_ascii=False, indent=2)
        return "lookup_caching_strategy result:\n" + formatted_result

    if decision.action == "get_implementations":
        strategy_name = decision.arguments["strategy_name"]
        language = decision.arguments["language"]
        result = get_implementations(strategy_name, language)
        if result == NOT_FOUND:
            return f"get_implementations('{strategy_name}', '{language}') -> {NOT_FOUND}"
        formatted_result = json.dumps(result, ensure_ascii=False, indent=2)
        return "get_implementations result:\n" + formatted_result

    raise DecisionError(f"Unsupported action in dispatch: {decision.action}")


def run_agent(
    goal: str,
    *,
    decide_fn: DecisionFunction | None = None,
    max_steps: int = MAX_STEPS,
    max_llm_calls: int = MAX_LLM_CALLS,
    trace_dir: Path | None = None,
) -> AgentState:
    state = AgentState(goal=goal)
    chooser = decide_fn or decide_with_gemini

    while not state.finished:
        if state.step >= max_steps:
            state.finished = True
            state.stop_reason = "max_steps"
            state.final_answer = (
                f"The agent stopped because it reached the step limit ({max_steps}) "
                "without producing a final answer."
            )
            break

        if state.llm_calls >= max_llm_calls:
            state.finished = True
            state.stop_reason = "max_llm_calls"
            state.final_answer = (
                f"The agent stopped because it reached the LLM call limit ({max_llm_calls}) "
                "without producing a final answer."
            )
            break

        state.step += 1
        decision: Decision | None = None
        started = time.perf_counter()

        try:
            state.llm_calls += 1
            decision = validate_decision(chooser(state.goal, state.observations, state.step, max_steps))
            outcome = dispatch_action(state, decision)
            record = {
                "step": state.step,
                "action": decision.action,
                "arguments": decision.arguments,
                "decision_summary": decision.decision_summary,
            }
        except (DecisionError, KeyError, TypeError, ValueError, AttributeError) as error:
            decision = Decision(
                action="rejected",
                arguments={},
                decision_summary=f"Decision error: {error}",
            )
            outcome = f"ERROR: {error}"
            record = {
                "step": state.step,
                "action": "rejected",
                "arguments": None,
                "decision_summary": "",
                "rejected": {
                    "action": decision.action,
                    "arguments": decision.arguments,
                    "decision_summary": decision.decision_summary,
                },
            }

        record["observation"] = outcome
        record["seconds"] = round(time.perf_counter() - started, 2)
        state.trace.append(record)
        if outcome is not None:
            state.observations.append(outcome)

    save_trace(state, trace_dir=trace_dir)
    return state


def save_trace(state: AgentState, *, trace_dir: Path | None = None) -> Path:
    root_dir = Path(__file__).resolve().parents[1]
    output_dir = trace_dir or root_dir / "traces"
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + f"-{uuid4().hex[:8]}.json"
    trace_payload = {
        "goal": state.goal,
        "created_at": datetime.now(UTC).isoformat(),
        "stop_reason": state.stop_reason,
        "steps": state.step,
        "llm_calls": state.llm_calls,
        "final_answer": state.final_answer,
        "trace": state.trace,
    }
    trace_path = output_dir / file_name
    trace_path.write_text(json.dumps(trace_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return trace_path