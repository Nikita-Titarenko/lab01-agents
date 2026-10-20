from __future__ import annotations

"""Базова лінія: один виклик LLM без циклу, дій і середовища."""

from agent.errors import DecisionError
from agent.reasoning import MODEL, get_client

BASELINE_SYSTEM_PROMPT = (
    "Answer the user in Ukrainian. "
    "At the end of your answer, clearly state where the information came from "
    "and specify the exact source of the data used."
)


def one_shot_answer(goal: str) -> str:
    from google.genai import types

    response = get_client().models.generate_content(
        model=MODEL,
        contents=goal,
        config=types.GenerateContentConfig(system_instruction=BASELINE_SYSTEM_PROMPT),
    )
    text = getattr(response, "text", None)
    if not isinstance(text, str) or not text.strip():
        raise DecisionError("Gemini returned an empty response in one-shot mode.")
    return text