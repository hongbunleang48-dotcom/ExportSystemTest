"""config.py

Application Configuration module.
Implements environment-specific configurations using Clean Architecture principles.
"""

import os


class Config:
    """Base configuration with safe default settings."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "expert-system-clinical-triage-secret-2026")
    JSON_SORT_KEYS = False
    TESTING = False
    DEBUG = False


class DevelopmentConfig(Config):
    """Configuration for local development."""
    DEBUG = True


class TestingConfig(Config):
    """Configuration for automated testing."""
    TESTING = True
    DEBUG = False


class ProductionConfig(Config):
    """Configuration for production deployment."""
    DEBUG = False
    TESTING = False
    # In production, SECRET_KEY should be set via environment variable
    SECRET_KEY = os.environ.get("SECRET_KEY", "prod-strict-expert-key-fallback")


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
