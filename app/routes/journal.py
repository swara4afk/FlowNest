"""
Journal blueprint — Daily Entries + Reflection Notes.

Structurally similar to Tasks (list / create / view / edit / delete),
but journal entries have two free-text bodies: `content` (the entry
itself) and `reflection` (a lighter "what went well / what to
improve" prompt), plus an optional `title`.
"""

from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.journal import JournalEntry

journal_bp = Blueprint("journal", __name__, url_prefix="/journal")


def _parse_date(raw: str, default: date) -> date:
    if not raw:
        return default
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return default


def _get_owned_entry_or_404(entry_id: int) -> JournalEntry:
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        abort(404)
    return entry


@journal_bp.route("/")
@login_required
def index():
    entries = (
        JournalEntry.query.filter_by(user_id=current_user.id)
        .order_by(JournalEntry.entry_date.desc(), JournalEntry.created_at.desc())
        .all()
    )
    return render_template("journal/index.html", entries=entries)


@journal_bp.route("/<int:entry_id>")
@login_required
def view(entry_id):
    entry = _get_owned_entry_or_404(entry_id)
    return render_template("journal/view.html", entry=entry)


@journal_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        entry_date = _parse_date(request.form.get("entry_date", ""), date.today())
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        reflection = request.form.get("reflection", "").strip()

        if not content:
            flash("Journal entry can't be empty.", "danger")
            return render_template(
                "journal/form.html",
                mode="create",
                entry={"title": title, "content": content, "reflection": reflection},
                entry_date_value=request.form.get("entry_date", ""),
            )

        entry = JournalEntry(
            user_id=current_user.id,
            entry_date=entry_date,
            title=title or None,
            content=content,
            reflection=reflection or None,
        )
        db.session.add(entry)
        db.session.commit()
        flash("Journal entry saved.", "success")
        return redirect(url_for("journal.view", entry_id=entry.id))

    return render_template(
        "journal/form.html", mode="create", entry=None, entry_date_value=date.today().isoformat()
    )


@journal_bp.route("/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit(entry_id):
    entry = _get_owned_entry_or_404(entry_id)

    if request.method == "POST":
        entry_date = _parse_date(request.form.get("entry_date", ""), entry.entry_date)
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        reflection = request.form.get("reflection", "").strip()

        if not content:
            flash("Journal entry can't be empty.", "danger")
            return render_template(
                "journal/form.html",
                mode="edit",
                entry=entry,
                entry_date_value=request.form.get("entry_date", ""),
            )

        entry.entry_date = entry_date
        entry.title = title or None
        entry.content = content
        entry.reflection = reflection or None
        db.session.commit()
        flash("Journal entry updated.", "success")
        return redirect(url_for("journal.view", entry_id=entry.id))

    return render_template(
        "journal/form.html", mode="edit", entry=entry, entry_date_value=entry.entry_date.isoformat()
    )


@journal_bp.route("/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete(entry_id):
    entry = _get_owned_entry_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash("Journal entry deleted.", "info")
    return redirect(url_for("journal.index"))
