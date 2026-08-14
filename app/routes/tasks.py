"""
Tasks blueprint — the Task Manager module.

Full CRUD scoped to the logged-in user. Every read/update/delete
query filters by `user_id=current_user.id` (or checks ownership
before mutating) so one user can never see or touch another
user's tasks, even by guessing an ID in the URL.
"""

from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

VALID_PRIORITIES = {"Low", "Medium", "High"}
VALID_FILTERS = {"all", "pending", "completed"}


def _get_owned_task_or_404(task_id: int) -> Task:
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(404)  # 404 rather than 403 — don't reveal the task exists
    return task


def _parse_due_date(raw: str):
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return None


@tasks_bp.route("/")
@login_required
def index():
    status_filter = request.args.get("status", "all")
    if status_filter not in VALID_FILTERS:
        status_filter = "all"

    query = Task.query.filter_by(user_id=current_user.id)
    if status_filter == "pending":
        query = query.filter_by(is_completed=False)
    elif status_filter == "completed":
        query = query.filter_by(is_completed=True)

    # Incomplete tasks first, then soonest due date, nulls last, then title
    tasks = query.order_by(
        Task.is_completed.asc(),
        Task.due_date.is_(None).asc(),
        Task.due_date.asc(),
        Task.title.asc(),
    ).all()

    total = Task.query.filter_by(user_id=current_user.id).count()
    completed = Task.query.filter_by(user_id=current_user.id, is_completed=True).count()

    return render_template(
        "tasks/index.html",
        tasks=tasks,
        status_filter=status_filter,
        total=total,
        completed=completed,
        today=date.today(),
    )


@tasks_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Medium")
        due_date = _parse_due_date(request.form.get("due_date", ""))

        errors = []
        if not title:
            errors.append("Task title is required.")
        if priority not in VALID_PRIORITIES:
            priority = "Medium"

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                "tasks/form.html",
                mode="create",
                task={
                    "title": title,
                    "description": description,
                    "priority": priority,
                },
                due_date_value=request.form.get("due_date", ""),
            )

        task = Task(
            user_id=current_user.id,
            title=title,
            description=description or None,
            priority=priority,
            due_date=due_date,
        )
        db.session.add(task)
        db.session.commit()
        flash("Task created.", "success")
        return redirect(url_for("tasks.index"))

    return render_template("tasks/form.html", mode="create", task=None, due_date_value="")


@tasks_bp.route("/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit(task_id):
    task = _get_owned_task_or_404(task_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Medium")
        due_date = _parse_due_date(request.form.get("due_date", ""))

        if not title:
            flash("Task title is required.", "danger")
            return render_template(
                "tasks/form.html",
                mode="edit",
                task=task,
                due_date_value=request.form.get("due_date", ""),
            )

        if priority not in VALID_PRIORITIES:
            priority = "Medium"

        task.title = title
        task.description = description or None
        task.priority = priority
        task.due_date = due_date
        db.session.commit()
        flash("Task updated.", "success")
        return redirect(url_for("tasks.index"))

    return render_template(
        "tasks/form.html",
        mode="edit",
        task=task,
        due_date_value=task.due_date.strftime("%Y-%m-%d") if task.due_date else "",
    )


@tasks_bp.route("/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle(task_id):
    task = _get_owned_task_or_404(task_id)
    task.is_completed = not task.is_completed
    db.session.commit()
    return redirect(request.referrer or url_for("tasks.index"))


@tasks_bp.route("/<int:task_id>/delete", methods=["POST"])
@login_required
def delete(task_id):
    task = _get_owned_task_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted.", "info")
    return redirect(url_for("tasks.index"))
