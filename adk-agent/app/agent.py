from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

MODEL_BACKEND = os.getenv("MODEL_BACKEND", "gemini").strip().lower()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", os.getenv("OLLAMA_MODEL", "llama3.1:8b"))
OPENAI_BASE_URL = os.getenv(
    "OPENAI_BASE_URL", os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", os.getenv("OLLAMA_API_KEY", "ollama"))

INSTRUCTION = """
ROLE: Educational AI agent for caching strategies in distributed systems.
PURPOSE: Answer questions about caching strategies only from verified facts returned by the tools.
LANGUAGE: Always answer in Ukrainian unless the user explicitly requests another language. Even if tool results are in English, paraphrase the final answer in natural Ukrainian.
BEHAVIOR RULES:
1. Before answering about a specific strategy, call lookup_caching_strategy for each mentioned strategy.
2. If a tool result is NOT_FOUND, explicitly say that verified data is unavailable and do not invent facts.
3. Use get_implementations when the user asks about framework or library implementations for a strategy and language.
4. In strategy comparisons, use only facts returned by lookup_caching_strategy or get_implementations.
5. Do not call the same tool again with the same argument unless the user changes the request.
6. Keep explanations concise and technically precise.
7. Write the final user-facing answer in Ukrainian Cyrillic, not in English transliteration.
LIMITATIONS: Do not invent sources, do not use knowledge outside the registered tools for concrete strategy claims, do not leave the final answer in English unless the user explicitly asked for English, and do not perform actions for which no tool exists.
""".strip()

try:
    from google.adk.agents import Agent
    from google.adk.apps import App
    from google.adk.models import Gemini
    from google.genai import types

    from app.environment import get_implementations, lookup_caching_strategy

    def _build_model() -> Any:
        if MODEL_BACKEND == "gemini":
            return Gemini(
                model=GEMINI_MODEL,
                retry_options=types.HttpRetryOptions(attempts=3),
            )

        if MODEL_BACKEND in {"openai", "openai_compatible", "ollama"}:
            # Ollama exposes an OpenAI-compatible endpoint at /v1.
            from google.adk.integrations.openai import OpenAILlm

            return OpenAILlm(
                model=OPENAI_MODEL,
                base_url=OPENAI_BASE_URL,
                api_key=OPENAI_API_KEY,
            )

        raise ValueError(
            "Unsupported MODEL_BACKEND. Use one of: gemini, openai_compatible, ollama"
        )

    root_agent = Agent(
        name="root_agent",
        model=_build_model(),
        instruction=INSTRUCTION,
        tools=[lookup_caching_strategy, get_implementations],
    )

    app = App(root_agent=root_agent, name="app")
except ImportError:  # pragma: no cover - allows offline editing without ADK installed
    root_agent = None
    app = None
