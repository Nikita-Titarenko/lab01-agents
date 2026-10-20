from app.environment import (
    NOT_FOUND,
    _general_method,
    get_implementations,
    lookup_caching_strategy,
)


def test_lookup_existing_strategy() -> None:
    result = lookup_caching_strategy("refresh-ahead")
    assert result != NOT_FOUND
    assert isinstance(result, dict)
    assert result["identifier"] == "refresh_ahead"


def test_lookup_missing_strategy() -> None:
    assert lookup_caching_strategy("unknown-cache-style") == NOT_FOUND


def test_general_method_returns_full_strategy_object() -> None:
    result = _general_method("refresh-ahead")
    assert result != NOT_FOUND
    assert "implementations" in result
    assert "tradeoffs" in result
    assert "sources" in result
    assert "implementation_sources" in result
    assert "description" in result

    reduced = lookup_caching_strategy("refresh-ahead")
    assert reduced != NOT_FOUND
    assert "tradeoffs" in reduced
    assert "sources" in reduced
    assert "implementations" not in reduced
    assert "implementation_sources" not in reduced


def test_get_implementations() -> None:
    result = get_implementations("refresh-ahead", "python")
    assert result != NOT_FOUND
    assert isinstance(result, dict)
    assert result["language"] == "python"
    assert isinstance(result["implementations"], dict)
    assert result["implementation_sources"]
    sources = result["sources"]
    assert isinstance(sources, list)
    assert sources
    assert any(isinstance(source, str) and "AWS" in source for source in sources)
