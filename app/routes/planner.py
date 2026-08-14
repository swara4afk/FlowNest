"""
Planner blueprint — Daily & Weekly Planner module.

Two read views (daily, weekly) share the same underlying
PlannerEntry model and CRUD endpoints. The "weekly" view is a
read/organize surface; entries are still created and edited through
the same create/edit/toggle/delete routes used by the daily view,
just with a `date` passed back so the redirect returns to the
correct day.
"""

from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.planner import PlannerEntry
from app.utils.dates import current_week_range

planner_bp = Blueprint("planner", __name__, url_prefix="/planner")


def _parse_date(raw: str, default: date) -> date:
    if not raw:
        return default
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return default


def _get_owned_entry_or_404(entry_id: int) -> PlannerEntry:
    entry = PlannerEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        abort(404)
    return entry


@planner_bp.route("/")
@login_required
def daily():
    selected_date = _parse_date(request.args.get("date", ""), date.today())

    entries = (
        PlannerEntry.query.filter_by(user_id=current_user.id, entry_date=selected_date)
        .order_by(PlannerEntry.time_slot.is_(None).asc(), PlannerEntry.time_slot.asc())
        .all()
    )

    return render_template(
        "planner/daily.html",
        entries=entries,
        selected_date=selected_date,
        prev_date=selected_date - timedelta(days=1),
        next_date=selected_date + timedelta(days=1),
        today=date.today(),
    )


@planner_bp.route("/week")
@login_required
def weekly():
    ref_date = _parse_date(request.args.get("start", ""), date.today())
    week_start, week_end = current_week_range(ref_date)

    entries = (
        PlannerEntry.query.filter(
            PlannerEntry.user_id == current_user.id,
            PlannerEntry.entry_date >= week_start,
            PlannerEntry.entry_date <= week_end,
        )
        .order_by(PlannerEntry.time_slot.is_(None).asc(), PlannerEntry.time_slot.asc())
        .all()
    )

    # Group entries by date for easy template rendering
    days = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_entries = [e for e in entries if e.entry_date == day]
        days.append({"date": day, "entries": day_entries})

    return render_template(
        "planner/weekly.html",
        days=days,
        week_start=week_start,
        week_end=week_end,
        prev_week=week_start - timedelta(days=7),
        next_week=week_start + timedelta(days=7),
        today=date.today(),
    )


@planner_bp.route("/create", methods=["POST"])
@login_required
def create():
    entry_date = _parse_date(request.form.get("entry_date", ""), date.today())
    time_slot = request.form.get("time_slot", "").strip() or None
    content = request.form.get("content", "").strip()
    redirect_to = request.form.get("redirect_to", "daily")

    if not content:
        flash("Planner entry can't be empty.", "danger")
    else:
        entry = PlannerEntry(
            user_id=current_user.id,
            entry_date=entry_date,
            time_slot=time_slot,
            content=content,
        )
        db.session.add(entry)
        db.session.commit()
        flash("Added to your planner.", "success")

    if redirect_to == "weekly":
        week_start, _ = current_week_range(entry_date)
        return redirect(url_for("planner.weekly", start=week_start.isoformat()))
    return redirect(url_for("planner.daily", date=entry_date.isoformat()))


@planner_bp.route("/<int:entry_id>/toggle", methods=["POST"])
@login_required
def toggle(entry_id):
    entry = _get_owned_entry_or_404(entry_id)
    entry.is_done = not entry.is_done
    db.session.commit()
    return redirect(request.referrer or url_for("planner.daily"))


@planner_bp.route("/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete(entry_id):
    entry = _get_owned_entry_or_404(entry_id)
    entry_date = entry.entry_date
    redirect_to = request.form.get("redirect_to", "daily")
    db.session.delete(entry)
    db.session.commit()
    flash("Entry removed.", "info")

    if redirect_to == "weekly":
        week_start, _ = current_week_range(entry_date)
        return redirect(url_for("planner.weekly", start=week_start.isoformat()))
    return redirect(url_for("planner.daily", date=entry_date.isoformat()))
