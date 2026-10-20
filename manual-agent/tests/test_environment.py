from agent.environment import NOT_FOUND, _general_method, get_implementations, lookup_caching_strategy


def test_lookup_existing_strategy_returns_reduced_facts() -> None:
    result = lookup_caching_strategy("write-through")
    assert result != NOT_FOUND
    assert result["identifier"] == "write_through"
    assert "synchronously persists" in result["write_path"]


def test_lookup_missing_strategy_returns_not_found() -> None:
    assert lookup_caching_strategy("random cache trick") == NOT_FOUND


def test_general_method_returns_full_strategy_object() -> None:
    result = _general_method("write-through")
    assert result != NOT_FOUND
    assert "implementations" in result
    assert "tradeoffs" in result
    assert "sources" in result
    assert "implementation_sources" in result
    assert "description" in result

    reduced = lookup_caching_strategy("write-through")
    assert reduced != NOT_FOUND
    assert "tradeoffs" in reduced
    assert "sources" in reduced
    assert "implementations" not in reduced
    assert "implementation_sources" not in reduced


def test_get_implementations_returns_language_specific_catalog() -> None:
    result = get_implementations("write-through", "c#")
    assert result != NOT_FOUND
    assert result["language"] == "c#"
    assert "tradeoffs" not in result
    assert isinstance(result["implementations"], dict)
    assert result["implementation_sources"]
    assert result["sources"]
    assert any("Microsoft Learn" in source for source in result["sources"])