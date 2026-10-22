"""app/__init__.py

Flask Application Factory.
Initializes the web layer, registers blueprints, sets up configurations,
and injects lightweight pure-Python i18n translation context processor.
"""

import os
from typing import Optional, Union

from flask import Flask, session

from config import Config, config_by_name
from app.core.i18n import get_text, DEFAULT_LOCALE


def create_app(config_name: Optional[Union[str, type[Config]]] = None) -> Flask:
    """Application factory for the Clinical Expert System.
    
    Args:
        config_name: Name of the configuration profile ('development', 'testing', 'production')
                     or a Config class object. Defaults to FLASK_CONFIG env var or 'development'.
                     
    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)

    # Determine configuration class
    if config_name is None:
        env_profile = os.environ.get("FLASK_CONFIG", "development")
        config_class = config_by_name.get(env_profile, config_by_name["default"])
    elif isinstance(config_name, str):
        config_class = config_by_name.get(config_name, config_by_name["default"])
    else:
        config_class = config_name

    app.config.from_object(config_class)

    # Inject i18n translation helper into template context
    @app.context_processor
    def inject_i18n():
        current_locale = session.get("locale", DEFAULT_LOCALE)
        return {
            "current_locale": current_locale,
            "_t": lambda key, default=None, **kwargs: get_text(
                key=key,
                locale=session.get("locale", DEFAULT_LOCALE),
                default=default,
                **kwargs,
            ),
        }

    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
