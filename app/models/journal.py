"""JournalEntry model — backs the Journal module (daily entries + reflection)."""

from datetime import datetime, timezone
from app.extensions import db


class JournalEntry(db.Model):
    __tablename__ = "journal_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    entry_date = db.Column(db.Date, nullable=False, index=True)
    title = db.Column(db.String(150), nullable=True)
    content = db.Column(db.Text, nullable=False)
    reflection = db.Column(db.Text, nullable=True)  # "What went well / what to improve"

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<JournalEntry {self.entry_date}>"
