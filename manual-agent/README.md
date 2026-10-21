# manual-agent

Minimal educational AI agent for the topic of caching strategies.

## Run

The CLI prints the answer to stdout and writes the total request execution time to stderr in the format:

```text
[timing] Request execution time: 2.34 seconds
```

```bash
uv run python main.py "Опиши стратегію Cache-Aside."
uv run python main.py "Опиши стратегію Cache-Aside." --mode oneshot
```

## Tests

```bash
uv run pytest
```

## Report

- [ЛР_№1_ПЗПІ-23-1_Тітаренко_М_С.pdf](../ЛР_№1_ПЗПІ-23-1_Тітаренко_М_С.pdf)