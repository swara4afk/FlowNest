"""
Application configuration.

Uses a base Config class with environment-specific overrides.
Keeping config in one place makes it easy to see every tunable
setting and to add new environments (staging, production) later.
"""

import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    """Shared configuration for all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'database', 'flownest.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session / cookie settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # App-level constants
    TASK_PRIORITIES = ["Low", "Medium", "High"]
    MOOD_OPTIONS = [
        {"key": "great", "label": "Great", "emoji": "😄"},
        {"key": "good", "label": "Good", "emoji": "🙂"},
        {"key": "okay", "label": "Okay", "emoji": "😐"},
        {"key": "low", "label": "Low", "emoji": "😔"},
        {"key": "stressed", "label": "Stressed", "emoji": "😣"},
    ]


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
