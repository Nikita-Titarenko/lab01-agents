import os

import pytest

from app.agent import app, root_agent

pytest.importorskip(
    "google.adk", reason="google-adk is not installed in this environment"
)


def _has_backend_credentials() -> bool:
    backend = os.getenv("MODEL_BACKEND", "gemini").strip().lower()
    if backend == "gemini":
        return bool(os.getenv("GEMINI_API_KEY"))
    if backend in {"ollama", "openai_compatible", "openai"}:
        return bool(os.getenv("OPENAI_BASE_URL") and os.getenv("OPENAI_MODEL"))
    return False


@pytest.mark.skipif(
    not _has_backend_credentials(),
    reason="Model backend credentials are required for live ADK integration checks",
)
def test_adk_app_is_configured() -> None:
    assert app is not None
    assert root_agent is not None
    assert root_agent.name == "root_agent"
