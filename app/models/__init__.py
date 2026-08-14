"""
Models package.

Importing all models here ensures SQLAlchemy registers every table
with db.metadata when `db.create_all()` runs in the app factory —
even though nothing in this file appears to be "used" directly.
"""

from app.models.user import User
from app.models.task import Task
from app.models.planner import PlannerEntry
from app.models.journal import JournalEntry
from app.models.mood import MoodEntry

__all__ = ["User", "Task", "PlannerEntry", "JournalEntry", "MoodEntry"]
