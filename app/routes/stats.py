"""
Statistics blueprint.

Pulls aggregate data from Tasks, Planner, Journal, and Mood to give
students a "how am I actually doing" view. Everything here is
read-only and computed on request — no separate stats table, since
the source data is small enough per user that live aggregation is
simpler and always correct (no risk of stale cached numbers).

Note: Task has no dedicated `completed_at` column, so the daily
completions trend uses `updated_at` as a reasonable proxy for
"when this task was last marked complete." This is called out in
the README as a known simplification.
"""

from datetime import date, timedelta
from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user

from app.models.task import Task
from app.models.planner import PlannerEntry
from app.models.journal import JournalEntry
from app.models.mood import MoodEntry

stats_bp = Blueprint("stats", __name__, url_prefix="/statistics")


def _last_n_days(n: int, today: date) -> list[date]:
    return [today - timedelta(days=i) for i in range(n - 1, -1, -1)]


@stats_bp.route("/")
@login_required
def index():
    today = date.today()
    user_id = current_user.id

    # --- Task overview ---
    total_tasks = Task.query.filter_by(user_id=user_id).count()
    completed_tasks = Task.query.filter_by(user_id=user_id, is_completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    overdue_tasks = Task.query.filter(
        Task.user_id == user_id,
        Task.is_completed.is_(False),
        Task.due_date.isnot(None),
        Task.due_date < today,
    ).count()
    completion_rate = round((completed_tasks / total_tasks) * 100) if total_tasks else 0

    # --- Priority breakdown ---
    priority_breakdown = []
    for priority in ["High", "Medium", "Low"]:
        p_total = Task.query.filter_by(user_id=user_id, priority=priority).count()
        p_completed = Task.query.filter_by(user_id=user_id, priority=priority, is_completed=True).count()
        priority_breakdown.append({
            "priority": priority,
            "total": p_total,
            "completed": p_completed,
            "rate": round((p_completed / p_total) * 100) if p_total else 0,
        })

    # --- Last 7 days: tasks completed per day (using updated_at as completion proxy) ---
    days = _last_n_days(7, today)
    all_completed = Task.query.filter_by(user_id=user_id, is_completed=True).all()
    completions_by_date = {d: 0 for d in days}
    for t in all_completed:
        completed_date = t.updated_at.date() if t.updated_at else None
        if completed_date in completions_by_date:
            completions_by_date[completed_date] += 1
    daily_completions = [{"date": d, "count": completions_by_date[d]} for d in days]
    max_daily = max((d["count"] for d in daily_completions), default=0)

    # --- Last 7 days: mood trend ---
    mood_lookup = {m["key"]: m for m in current_app.config["MOOD_OPTIONS"]}
    mood_entries = {
        e.entry_date: e
        for e in MoodEntry.query.filter(
            MoodEntry.user_id == user_id,
            MoodEntry.entry_date >= days[0],
            MoodEntry.entry_date <= days[-1],
        ).all()
    }
    mood_trend = []
    for d in days:
        entry = mood_entries.get(d)
        mood_trend.append({
            "date": d,
            "option": mood_lookup.get(entry.mood) if entry else None,
        })

    # --- Planner: this week's completion rate ---
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_planner_entries = PlannerEntry.query.filter(
        PlannerEntry.user_id == user_id,
        PlannerEntry.entry_date >= week_start,
        PlannerEntry.entry_date <= week_end,
    ).all()
    planner_total = len(week_planner_entries)
    planner_done = sum(1 for e in week_planner_entries if e.is_done)
    planner_rate = round((planner_done / planner_total) * 100) if planner_total else 0

    # --- Journal: total entries + current daily streak ---
    journal_dates = {
        e.entry_date for e in JournalEntry.query.filter_by(user_id=user_id).all()
    }
    journal_count = len(journal_dates)
    streak = 0
    cursor = today
    while cursor in journal_dates:
        streak += 1
        cursor -= timedelta(days=1)

    return render_template(
        "stats/index.html",
        stats={
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "overdue_tasks": overdue_tasks,
            "completion_rate": completion_rate,
        },
        priority_breakdown=priority_breakdown,
        daily_completions=daily_completions,
        max_daily=max_daily,
        mood_trend=mood_trend,
        planner_total=planner_total,
        planner_done=planner_done,
        planner_rate=planner_rate,
        journal_count=journal_count,
        journal_streak=streak,
    )
