from backend.app.config import settings


def test_configuration_loads() -> None:
    assert settings.app_name == "AI Call Center Training Agent"
    assert settings.app_env == "development"
    assert settings.database_url