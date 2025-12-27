import os
import sys

# Ensure the Flask app folder is importable when running from repo root.
APP_DIR = os.path.join(
    os.path.dirname(__file__), "solar_prescription", "solar_prescription"
)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from app import app  # noqa: E402
