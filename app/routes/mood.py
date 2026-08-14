"""
Mood Tracker blueprint.

Design choice: one mood entry per user per day. Logging a mood for
a date that already has an entry updates it in place (upsert)
rather than creating a duplicate — mood tracking works best as a
daily check-in, not an open log, and this keeps the history clean
for the trend/summary work Statistics will do later.
"""

from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user

from app.extensions import db
from app.models.mood import MoodEntry

mood_bp = Blueprint("mood", __name__, url_prefix="/mood")


def _parse_date(raw: str, default: date) -> date:
    if not raw:
        return default
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return default


def _get_owned_entry_or_404(entry_id: int) -> MoodEntry:
    entry = MoodEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        abort(404)
    return entry


@mood_bp.route("/")
@login_required
def index():
    today = date.today()
    mood_options = current_app.config["MOOD_OPTIONS"]
    mood_lookup = {m["key"]: m for m in mood_options}

    todays_entry = MoodEntry.query.filter_by(user_id=current_user.id, entry_date=today).first()

    history = (
        MoodEntry.query.filter_by(user_id=current_user.id)
        .order_by(MoodEntry.entry_date.desc())
        .limit(30)
        .all()
    )

    return render_template(
        "mood/index.html",
        today=today,
        mood_options=mood_options,
        mood_lookup=mood_lookup,
        todays_entry=todays_entry,
        history=history,
    )


@mood_bp.route("/log", methods=["POST"])
@login_required
def log():
    entry_date = _parse_date(request.form.get("entry_date", ""), date.today())
    mood = request.form.get("mood", "")
    notes = request.form.get("notes", "").strip()

    valid_keys = {m["key"] for m in current_app.config["MOOD_OPTIONS"]}
    if mood not in valid_keys:
        flash("Please select a valid mood.", "danger")
        return redirect(url_for("mood.index"))

    existing = MoodEntry.query.filter_by(user_id=current_user.id, entry_date=entry_date).first()
    if existing:
        existing.mood = mood
        existing.notes = notes or None
        flash("Mood updated for this day.", "success")
    else:
        db.session.add(
            MoodEntry(user_id=current_user.id, entry_date=entry_date, mood=mood, notes=notes or None)
        )
        flash("Mood logged.", "success")

    db.session.commit()
    return redirect(url_for("mood.index"))


@mood_bp.route("/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete(entry_id):
    entry = _get_owned_entry_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash("Mood entry removed.", "info")
    return redirect(url_for("mood.index"))
