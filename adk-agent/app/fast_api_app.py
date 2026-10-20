"""Real ASGI adapter for the Google ADK app.

The ADK `App` object is not itself callable by uvicorn. We adapt it through the
official Google ADK FastAPI factory so the framework handles HTTP/session logic.
"""

from __future__ import annotations

from google.adk.cli.fast_api import get_fast_api_app

app = get_fast_api_app(
    agents_dir=".",
    web=True,
    a2a=False,
    host="127.0.0.1",
    port=18080,
    bind_host="127.0.0.1",
    auto_create_session=True,
    allow_origins=["*"],
)

__all__ = ["app"]
