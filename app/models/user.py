"""User model — the root entity every other table relates back to."""

from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships — cascade delete so removing a user cleans up their data
    tasks = db.relationship("Task", backref="owner", lazy=True, cascade="all, delete-orphan")
    planner_entries = db.relationship("PlannerEntry", backref="owner", lazy=True, cascade="all, delete-orphan")
    journal_entries = db.relationship("JournalEntry", backref="owner", lazy=True, cascade="all, delete-orphan")
    mood_entries = db.relationship("MoodEntry", backref="owner", lazy=True, cascade="all, delete-orphan")

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f"<User {self.email}>"


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))
