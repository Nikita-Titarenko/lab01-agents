from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Decision:
    action: str
    arguments: dict[str, str]
    decision_summary: str


@dataclass
class AgentState:
    goal: str
    observations: list[str] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)
    step: int = 0
    llm_calls: int = 0
    finished: bool = False
    final_answer: str | None = None
    stop_reason: str | None = None