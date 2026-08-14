"""
Dashboard blueprint.

The dashboard is a read-only aggregation view: welcome/greeting,
quick stats pulled from Tasks/Planner/Mood, and a short "what's
next" list. It intentionally has no create/edit logic of its own —
that lives in each module's own blueprint (Tasks, Planner, ...).
"""

from datetime import date
from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user

from app.models.task import Task
from app.models.planner import PlannerEntry
from app.models.mood import MoodEntry
from app.utils.dates import get_greeting

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    today = date.today()
    user_id = current_user.id

    # --- Task stats ---
    total_tasks = Task.query.filter_by(user_id=user_id).count()
    completed_tasks = Task.query.filter_by(user_id=user_id, is_completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    due_today_tasks = Task.query.filter_by(
        user_id=user_id, is_completed=False, due_date=today
    ).count()
    overdue_tasks = Task.query.filter(
        Task.user_id == user_id,
        Task.is_completed.is_(False),
        Task.due_date.isnot(None),
        Task.due_date < today,
    ).count()

    completion_rate = round((completed_tasks / total_tasks) * 100) if total_tasks else 0

    # --- Today's planner items ---
    todays_plan = (
        PlannerEntry.query.filter_by(user_id=user_id, entry_date=today)
        .order_by(PlannerEntry.time_slot.asc())
        .all()
    )

    # --- Upcoming tasks (next 5 by due date, soonest first, incomplete only) ---
    upcoming_tasks = (
        Task.query.filter(
            Task.user_id == user_id,
            Task.is_completed.is_(False),
            Task.due_date.isnot(None),
        )
        .order_by(Task.due_date.asc())
        .limit(5)
        .all()
    )

    # --- Most recent mood entry ---
    latest_mood = (
        MoodEntry.query.filter_by(user_id=user_id)
        .order_by(MoodEntry.entry_date.desc(), MoodEntry.created_at.desc())
        .first()
    )

    mood_lookup = {m["key"]: m for m in current_app.config["MOOD_OPTIONS"]}
    latest_mood_display = mood_lookup.get(latest_mood.mood) if latest_mood else None

    stats = {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "due_today_tasks": due_today_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_rate": completion_rate,
    }

    return render_template(
        "dashboard/index.html",
        greeting=get_greeting(),
        today=today,
        stats=stats,
        todays_plan=todays_plan,
        upcoming_tasks=upcoming_tasks,
        latest_mood=latest_mood,
        latest_mood_display=latest_mood_display,
    )
