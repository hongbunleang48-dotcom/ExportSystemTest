"""run.py

Execution entry point for the Clinical Expert System.
Boots the Flask application server with development settings.
"""

import os
from app import create_app

# Load configuration profile from environment or default to development
config_name = os.environ.get("FLASK_CONFIG", "development")
app = create_app(config_name)

if __name__ == "__main__":
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ["1", "true", "yes"]

    print(f"[*] Starting Clinical Triage Expert System on http://{host}:{port}")
    print(f"[*] Mode: {config_name.upper()} (debug={debug})")
    app.run(host=host, port=port, debug=debug)
