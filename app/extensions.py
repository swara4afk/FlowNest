"""
Centralized Flask extension instances.

Extensions are created here (unbound) and initialized inside the
app factory with app.init_app(). This pattern avoids circular
imports between app/__init__.py and the model/route modules.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

# Where Flask-Login redirects unauthenticated users
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access FlowNest."
login_manager.login_message_category = "info"
