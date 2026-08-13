"""MoodEntry model — backs the Mood Tracker module."""

from datetime import datetime, timezone
from app.extensions import db


class MoodEntry(db.Model):
    __tablename__ = "mood_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    entry_date = db.Column(db.Date, nullable=False, index=True)
    mood = db.Column(db.String(20), nullable=False)  # matches Config.MOOD_OPTIONS keys
    notes = db.Column(db.String(300), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<MoodEntry {self.entry_date} {self.mood}>"
