"""Date and greeting helpers shared across modules."""

from datetime import datetime, date, timedelta


def get_greeting(now: datetime = None) -> str:
    """Return a time-of-day greeting."""
    now = now or datetime.now()
    hour = now.hour
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


def current_week_range(today: date = None) -> tuple[date, date]:
    """Return (Monday, Sunday) of the week containing `today`."""
    today = today or date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end
