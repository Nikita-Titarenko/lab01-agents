# adk-agent

Google ADK version of the caching-strategies agent from Part A.

## Structure

- `app/agent.py` defines the ADK agent, model backend selection, instruction, and tools.
- `app/environment.py` contains verified facts and deterministic helper tools.
- `tests/unit` contains offline-safe tests for deterministic logic.
- `tests/integration` contains live checks that require `google-adk` and credentials for the selected model backend.

## Model configuration

### Option A: Gemini (default)

Use AI Studio authentication in `.env`:

```env
# GOOGLE_CLOUD_PROJECT=
# GOOGLE_CLOUD_LOCATION=
MODEL_BACKEND="gemini"
GEMINI_API_KEY="YOUR_KEY"
GEMINI_MODEL="gemini-3.8-flash"
```

### Option B: Local model via Ollama

1. Start Ollama locally: `ollama serve`.
2. Pull a model, for example: `ollama pull llama3.1:8b`.
3. Configure `.env`:

```env
MODEL_BACKEND="ollama"
OPENAI_BASE_URL="http://127.0.0.1:11434/v1"
OPENAI_MODEL="llama3.1:8b"
# Ollama ignores API key, but OpenAI-compatible clients expect a value.
OPENAI_API_KEY="ollama"
```

`MODEL_BACKEND="openai_compatible"` also works for other OpenAI-compatible endpoints.

## Intended commands

```bash
agents-cli install
agents-cli lint
agents-cli run "Порівняй Cache-Aside і Write-Through"
agents-cli playground
uv run pytest tests/unit tests/integration
python3 adk-agent/send_prompt_to_local_agent.py "Порівняй Cache-Aside і Write-Through"
```

The ADK execution wrapper prints the answer to stdout and logs the total elapsed request time to stderr, for example:

```text
[timing] Request execution time: 2.34 seconds
```

## Current offline status

This repository currently includes a manual scaffold because `agents-cli` is not installed in the working shell. The project files are prepared to match the methodology structure, but live ADK execution still requires local installation of ADK tooling.

## Report

- [ЛР_№1_ПЗПІ-23-1_Тітаренко_М_С.pdf](../ЛР_№1_ПЗПІ-23-1_Тітаренко_М_С.pdf)