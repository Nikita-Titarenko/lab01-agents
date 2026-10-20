import json
import sys

import main as cli


class DummyState:
    def __init__(self, goal: str) -> None:
        self.goal = goal
        self.stop_reason = "finish"
        self.step = 1
        self.llm_calls = 1
        self.final_answer = "Done"
        self.observations = ["Observation"]
        self.trace = [{"step": 1, "seconds": 0.12}]


def test_agent_mode_logs_total_execution_time(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "run_agent", lambda goal, **kwargs: DummyState(goal))
    monkeypatch.setattr(sys, "argv", ["main.py", "Compare Cache-Aside and Write-Through"])

    cli.main()

    captured = capsys.readouterr()
    assert "Request execution time:" in captured.out or captured.err


def test_oneshot_mode_logs_total_execution_time(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "one_shot_answer", lambda goal: "Answer")
    monkeypatch.setattr(sys, "argv", ["main.py", "Assess 180 cache hits out of 200 requests", "--mode", "oneshot"])

    cli.main()

    captured = capsys.readouterr()
    assert "Request execution time:" in captured.out or captured.err
