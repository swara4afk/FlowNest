"""
Application factory.

create_app() builds and configures the Flask app so we can spin up
multiple instances (e.g. for testing) without shared global state.
Blueprints are registered here as each module is built; for now
only the health-check root route exists — real blueprints get
added module by module.
"""

import os
from flask import Flask, render_template

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
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.tasks import tasks_bp
    from app.routes.planner import planner_bp
    from app.routes.journal import journal_bp
    from app.routes.mood import mood_bp
    from app.routes.stats import stats_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(planner_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(mood_bp)
    app.register_blueprint(stats_bp)

    # Create tables if they don't exist yet (fine for SQLite portfolio project;
    # a real production app would use Flask-Migrate instead)
    with app.app_context():
        db.create_all()

    # Error handlers — styled pages instead of raw Flask debug output
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app
