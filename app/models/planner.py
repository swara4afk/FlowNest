"""PlannerEntry model — backs the Daily & Weekly Planner module.

A single row represents one time-blocked or note-style entry on a
given date. Weekly view groups entries client/server-side by the
ISO week of `entry_date`, so no separate weekly table is needed.
"""

from datetime import datetime, timezone
from app.extensions import db


class PlannerEntry(db.Model):
    __tablename__ = "planner_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    entry_date = db.Column(db.Date, nullable=False, index=True)
    time_slot = db.Column(db.String(20), nullable=True)  # e.g. "09:00 - 10:00"
    content = db.Column(db.String(300), nullable=False)
    is_done = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<PlannerEntry {self.entry_date} {self.content[:20]!r}>"
