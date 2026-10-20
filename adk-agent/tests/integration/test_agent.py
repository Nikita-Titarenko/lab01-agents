import os

import pytest

from app.agent import app, root_agent

pytest.importorskip(
    "google.adk", reason="google-adk is not installed in this environment"
)


@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY is required for live ADK integration checks",
)
def test_adk_app_is_configured() -> None:
    assert app is not None
    assert root_agent is not None
    assert root_agent.name == "root_agent"
