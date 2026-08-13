"""
Application factory.

create_app() builds and configures the Flask app so we can spin up
multiple instances (e.g. for testing) without shared global state.
Blueprints are registered here as each module is built; for now
only the health-check root route exists — real blueprints get
added module by module.
"""

import os
from flask import Flask

from app.config import config_map
from app.extensions import db, login_manager


def create_app(env: str = None) -> Flask:
    env = env or os.environ.get("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config_map.get(env, config_map["default"]))

    # Ensure the database directory exists before SQLite tries to write there
    db_dir = os.path.join(app.root_path, "..", "database")
    os.makedirs(db_dir, exist_ok=True)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Import models so they register with SQLAlchemy metadata
    from app import models  # noqa: F401

    # Register blueprints (added incrementally as modules are built)
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    # Create tables if they don't exist yet (fine for SQLite portfolio project;
    # a real production app would use Flask-Migrate instead)
    with app.app_context():
        db.create_all()

    return app
