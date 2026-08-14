"""
Temporary root route for Milestone 1.

This just proves the app factory, config, DB, and base template are
wired correctly. It will be replaced by the real dashboard route in
the Dashboard milestone and by auth-gated redirects once login exists.
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return render_template("index.html")
