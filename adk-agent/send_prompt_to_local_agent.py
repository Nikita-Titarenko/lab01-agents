from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Mapping
from urllib import error, request

BASE_URL = "http://127.0.0.1:8080"
APP_NAME = "app"
USER_ID = "local-user"
SESSION_CREATE_PATH = f"/apps/{APP_NAME}/users/{USER_ID}/sessions"
RUN_PATH = "/run"
TIMEOUT_SECONDS = 60.0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a local session and send one prompt to the local ADK agent server.",
    )
    parser.add_argument("prompt", help="The user prompt to send to the local agent")
    return parser


def post_json(
    path: str, payload: Mapping[str, object]
) -> dict[str, object] | list[dict[str, object]]:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url=f"{BASE_URL}{path}",
        data=body,
        headers={
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
        text = response.read().decode("utf-8", errors="replace")
        return json.loads(text)


def create_session() -> str:
    response = post_json(SESSION_CREATE_PATH, {"state": {}})
    if not isinstance(response, dict):
        raise TypeError("Session creation response is not a JSON object.")

    session_id = response.get("id")
    if not isinstance(session_id, str) or not session_id.strip():
        raise ValueError(
            "Session creation response does not contain a valid session id."
        )
    return session_id


def extract_text_from_events(response: list[dict[str, object]]) -> str:
    text_candidates: list[str] = []

    for event in response:
        if not isinstance(event, dict):
            continue

        content = event.get("content")
        if not isinstance(content, dict):
            continue

        parts = content.get("parts")
        if not isinstance(parts, list):
            continue

        for part in parts:
            if not isinstance(part, dict):
                continue
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                text_candidates.append(text.strip())

    if not text_candidates:
        raise ValueError("Run response does not contain a text answer in any event.")

    return text_candidates[-1]


def send_prompt(prompt: str, session_id: str) -> str:
    payload = {
        "appName": APP_NAME,
        "userId": USER_ID,
        "sessionId": session_id,
        "newMessage": {
            "role": "user",
            "parts": [{"text": prompt}],
        },
    }
    response = post_json(RUN_PATH, payload)
    if not isinstance(response, list) or not response:
        raise ValueError("Run response is not a non-empty events list.")
    return extract_text_from_events(response)


def main() -> int:
    args = build_parser().parse_args()
    started = time.perf_counter()

    try:
        session_id = create_session()
        answer = send_prompt(args.prompt, session_id)
    except error.HTTPError as exc:
        elapsed = time.perf_counter() - started
        text = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP error {exc.code}: {text}", file=sys.stderr)
        print(f"[timing] Request failed after {elapsed:.2f} seconds", file=sys.stderr)
        return 1
    except error.URLError as exc:
        elapsed = time.perf_counter() - started
        print(f"Request to {BASE_URL} failed: {exc}", file=sys.stderr)
        print(f"[timing] Request failed after {elapsed:.2f} seconds", file=sys.stderr)
        return 1
    except (ValueError, json.JSONDecodeError) as exc:
        elapsed = time.perf_counter() - started
        print(f"Unexpected response: {exc}", file=sys.stderr)
        print(f"[timing] Request failed after {elapsed:.2f} seconds", file=sys.stderr)
        return 1

    print(answer)
    print(
        f"[timing] Request execution time: {time.perf_counter() - started:.2f} seconds",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
