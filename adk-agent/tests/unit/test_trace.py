from app.agent import app


def test_adk_app_is_exposed() -> None:
    assert app is not None
    assert getattr(app, "name", None) == "app"
