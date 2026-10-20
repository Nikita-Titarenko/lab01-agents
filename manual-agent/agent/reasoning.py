from __future__ import annotations

import os
import json

from dotenv import load_dotenv

from agent.errors import DecisionError
from agent.state import AgentState, Decision

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

_client = None

SYSTEM_INSTRUCTION = """
You are the reasoning component of a manual AI agent for caching strategies.
Return JSON only with keys: action, arguments, decision_summary.
Available actions:
- lookup_caching_strategy with arguments.strategy_name
- get_implementations with arguments.strategy_name and arguments.language
- finish with arguments.answer when the answer is complete
Rules:
- Use lookup_caching_strategy before answering factual questions about a specific strategy.
- Use get_implementations when the user asks about framework or library implementations for a strategy and language.
- If the user asks for comparison, you may call the lookup action multiple times across steps.
- Use only facts from VERIFIED OBSERVATIONS in the final answer.
- If an observation starts with NOT_FOUND, say the information is missing and do not invent it.
- If an observation starts with ERROR, fix your previous decision.
- Do not repeat a lookup that is already present in the observations.
- When you finish, write the user-facing answer in Ukrainian in arguments.answer.
- Keep decision_summary concise and grounded in observations.
""".strip()


def get_client():
    """Lazy client initialization keeps imports test-friendly when no key is configured."""

    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise DecisionError("GEMINI_API_KEY is not configured.")

        from google import genai

        _client = genai.Client(api_key=api_key)
    return _client


def build_observation(goal: str, observations: list[str], step: int, max_steps: int) -> str:
    known = "\n".join(f"- {item}" for item in observations) or "None yet."
    return (
        f"GOAL:\n{goal}\n\n"
        f"CURRENT STEP: {step} of {max_steps}\n\n"
        f"VERIFIED OBSERVATIONS:\n{known}\n\n"
        "AVAILABLE ACTIONS: lookup_caching_strategy(strategy_name), get_implementations(strategy_name, language), finish(answer)\n"
        "Choose the next action."
    )


def parse_decision(raw_text: str) -> Decision:
    try:
        payload = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as error:
        raise DecisionError(f"Model returned invalid JSON: {error}") from error

    if not isinstance(payload, dict):
        raise DecisionError("Model response must be a JSON object.")

    try:
        return Decision(
            action=payload["action"],
            arguments=payload.get("arguments", {}),
            decision_summary=payload.get("decision_summary", ""),
        )
    except KeyError as error:
        raise DecisionError(f"Model response is missing required field: {error}") from error


def decide_with_gemini(goal: str, observations: list[str], step: int, max_steps: int) -> Decision:
    from google.genai import types

    observation = build_observation(goal, observations, step, max_steps)
    response = get_client().models.generate_content(
        model=MODEL,
        contents=observation,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
        ),
    )
    raw_text = getattr(response, "text", "").strip()
    if not raw_text:
        raise DecisionError("Gemini returned an empty response.")
    return parse_decision(raw_text)