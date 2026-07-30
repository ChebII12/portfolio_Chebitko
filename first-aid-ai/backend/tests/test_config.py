import pytest

from app.core.config import Settings


@pytest.mark.parametrize(
    "secret_key",
    [
        "dev-secret-key-change-in-production",
        "change-me-in-production",
        "your-secret-key-generate-a-strong-random-key-in-production",
        "too-short",
    ],
)
def test_production_rejects_insecure_secret_keys(secret_key):
    with pytest.raises(ValueError, match="Production requires a strong SECRET_KEY"):
        Settings(app_environment="production", secret_key=secret_key)


def test_production_accepts_a_strong_non_placeholder_secret():
    settings = Settings(
        app_environment="production",
        secret_key="a-unique-production-signing-secret-with-32-plus-characters",
    )

    assert settings.app_environment == "production"
