from __future__ import annotations

import argparse
import sys
import time

from agent.errors import DecisionError
from agent.loop import MAX_LLM_CALLS, MAX_STEPS, run_agent
from baseline import one_shot_answer


def _print_agent_report(state) -> None:
    print(f"goal: {state.goal}")
    print(f"stop_reason: {state.stop_reason}")
    print(f"steps: {state.step}")
    print(f"llm_calls: {state.llm_calls}")

    print("\nfinal_answer:")
    print(state.final_answer or "")

    print("\nobservations:")
    if not state.observations:
        print("- (none)")
    else:
        for idx, observation in enumerate(state.observations, start=1):
            print(f"[{idx}]")
            print(observation)

    print("\ntrace:")
    if not state.trace:
        print("- (none)")
    else:
        for item in state.trace:
            step = item.get("step")
            action = item.get("action")
            seconds = item.get("seconds")
            print(f"- step={step}, action={action}, seconds={seconds}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manual AI agent for caching strategies")
    parser.add_argument("goal", help="User request for the agent")
    parser.add_argument(
        "--mode",
        choices=("agent", "oneshot"),
        default="agent",
        help="Agent loop or single LLM call baseline",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=MAX_STEPS,
        help="Maximum number of reasoning steps for agent mode",
    )
    parser.add_argument(
        "--max-llm-calls",
        type=int,
        default=MAX_LLM_CALLS,
        help="Maximum number of LLM calls for agent mode",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    started = time.perf_counter()

    try:
        if args.mode == "oneshot":
            answer = one_shot_answer(args.goal)
            print(answer)
            print(f"[timing] Request execution time: {time.perf_counter() - started:.2f} seconds", file=sys.stderr)
            return

        state = run_agent(args.goal, max_steps=args.max_steps, max_llm_calls=args.max_llm_calls)
        _print_agent_report(state)
        print(f"[timing] Request execution time: {time.perf_counter() - started:.2f} seconds", file=sys.stderr)
    except DecisionError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        print(f"[timing] Request failed after {time.perf_counter() - started:.2f} seconds", file=sys.stderr)
        raise SystemExit(1) from error
    except Exception as error:
        print(f"UNEXPECTED ERROR: {error}", file=sys.stderr)
        print(f"[timing] Request failed after {time.perf_counter() - started:.2f} seconds", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()