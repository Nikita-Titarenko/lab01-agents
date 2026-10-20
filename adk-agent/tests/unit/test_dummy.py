import pytest

from app.agent import app, root_agent

google_adk = pytest.importorskip(
    "google.adk", reason="google-adk is not installed in this environment"
)


def test_root_agent_is_defined() -> None:
    assert google_adk is not None
    assert root_agent is not None
    assert app is not None
