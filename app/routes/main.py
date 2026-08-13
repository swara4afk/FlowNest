"""
Temporary root route for Milestone 1.

This just proves the app factory, config, DB, and base template are
wired correctly. It will be replaced by the real dashboard route in
the Dashboard milestone and by auth-gated redirects once login exists.
"""

from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")
