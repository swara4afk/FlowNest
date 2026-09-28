# 🌿 FlowNest

**A Student Productivity & Personal Management System**

FlowNest is a full-stack web application that brings task management, planning, journaling, mood tracking, and progress statistics into a single, calm workspace — so students stop losing time switching between five different apps.

Built with **Python, Flask, and SQLite** using a modular, production-style architecture (blueprints, an app factory, normalized relational models, and a hand-written utility-first CSS design system).

---

## Table of Contents

- [Why FlowNest](#why-flownest)
- [Features](#features)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Installation](#installation)
- [Usage](#usage)
- [Design Decisions](#design-decisions)
- [Roadmap](#roadmap)
- [License](#license)

---

## Why FlowNest

Students often spread their academic and personal lives across a task app, a separate calendar, a notes app, a journaling app, and a mood tracker — and none of them talk to each other. FlowNest's dashboard pulls from all of it at once, so "how am I actually doing this week" is a single page load, not five app switches.

## Features

### 🏠 Dashboard
- Personalized daily greeting and date
- Quick stats: pending/completed tasks, completion rate, due-today, overdue
- Today's planner snapshot and next 5 upcoming tasks
- Latest mood check-in

### ✅ Task Manager
- Full CRUD (create, edit, delete, mark complete)
- Priority levels (Low / Medium / High) with color-coded badges
- Due dates with automatic overdue highlighting
- Filter by all / pending / completed

### 🗓️ Planner
- **Daily view** — time-blocked entries with prev/next day navigation
- **Weekly view** — 7-day grid with inline quick-add per day
- Shared data model between both views (no duplicated schema)

### 📓 Journal
- Daily entries with optional titles
- Separate reflection field ("what went well / what to improve")
- Full entry history with detail view

### 🙂 Mood Tracker
- One-tap daily mood check-in (5 mood states, with notes)
- Re-logging the same day updates that day's entry rather than duplicating it
- 30-day history view

### 📊 Statistics
- Task completion rate and priority breakdown
- 7-day completed-tasks trend (pure CSS bar chart — no charting library)
- 7-day mood trend
- Weekly planner completion rate
- Journal entry count and current daily streak

### 🔐 Authentication
- Secure registration and login (Flask-Login, hashed passwords via Werkzeug)
- All data is scoped per-user; every module checks ownership before returning or mutating a record

---

## Screenshots

> Add screenshots here once you've run the app locally — drop PNGs into a `docs/screenshots/` folder and reference them below.

| Dashboard | Task Manager | Planner |
|---|---|---|
| `flownest/docs/screenshots/dashboard.png` | `flownest/docs/screenshots/tasks.png` | `flownest/docs/screenshots/tasks.png` |

| Journal | Mood Tracker | Statistics |
|---|---|---|
| `flownest/docs/screenshots/dashboard.png` | `flownest/docs/screenshots/mood.png` | `flownest/docs/screenshots/statistics.png` |

---

## Tech Stack

**Backend**
- Python 3
- Flask (app factory + blueprints)
- Flask-SQLAlchemy (ORM)
- Flask-Login (session-based auth)
- Werkzeug (password hashing)

**Frontend**
- HTML5 (Jinja2 templating)
- CSS3 — hand-written, utility-first design system (no build step, no framework)
- Vanilla JavaScript only where genuinely needed (none required beyond native browser confirm dialogs)

**Database**
- SQLite (via SQLAlchemy ORM, normalized schema, cascade deletes)

**Tooling**
- Git & GitHub

---

## Project Structure

```
flownest/
├── app/
│   ├── __init__.py            # App factory — config, extensions, blueprints, error handlers
│   ├── config.py               # Environment-based configuration
│   ├── extensions.py           # Shared db / login_manager instances
│   │
│   ├── models/                 # SQLAlchemy models (one file per entity)
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── planner.py
│   │   ├── journal.py
│   │   └── mood.py
│   │
│   ├── routes/                 # Blueprints — one per module
│   │   ├── main.py             # Landing page / redirect logic
│   │   ├── auth.py             # Register / login / logout
│   │   ├── dashboard.py        # Read-only aggregated overview
│   │   ├── tasks.py            # Task Manager CRUD
│   │   ├── planner.py          # Daily & Weekly Planner
│   │   ├── journal.py          # Journal CRUD
│   │   ├── mood.py             # Mood Tracker (upsert-per-day)
│   │   └── stats.py            # Statistics / analytics
│   │
│   ├── utils/                  # Framework-free helpers
│   │   ├── validators.py       # Form validation
│   │   └── dates.py            # Greeting / week-range helpers
│   │
│   ├── templates/              # Jinja2 templates, mirrors routes/ structure
│   │   ├── base.html           # Shared layout, navbar, flash messages
│   │   ├── index.html          # Guest landing page
│   │   ├── errors/              # 404 / 500 pages
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── tasks/
│   │   ├── planner/
│   │   ├── journal/
│   │   ├── mood/
│   │   └── stats/
│   │
│   └── static/
│       ├── css/style.css       # Utility-first design system
│       ├── js/                 # Reserved for future use
│       └── images/             # Reserved for future use
│
├── database/                   # SQLite file lives here (gitignored)
├── run.py                      # Entry point
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## Database Schema

All tables are normalized and relate back to `users` with `ON DELETE CASCADE` semantics enforced at the ORM level.

| Table | Key Columns | Relationship |
|---|---|---|
| `users` | id, full_name, email (unique), password_hash | — |
| `tasks` | id, user_id, title, priority, due_date, is_completed | many-to-one → users |
| `planner_entries` | id, user_id, entry_date, time_slot, content, is_done | many-to-one → users |
| `journal_entries` | id, user_id, entry_date, title, content, reflection | many-to-one → users |
| `mood_entries` | id, user_id, entry_date, mood, notes | many-to-one → users |

---

## Installation

**Prerequisites:** Python 3.10+

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/flownest.git
cd flownest

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Configure environment variables
cp .env.example .env
# then edit .env and set a real SECRET_KEY

# 5. Run the app
python run.py
```

The app will be available at **https://flownest-o0v4.onrender.com/**. The SQLite database and all tables are created automatically on first run.

## Usage

1. Visit the homepage and click **Get Started** to create an account
2. You'll land on your **Dashboard** — empty at first, since it reflects your real data
3. Add a few tasks in **Tasks**, block out today in **Planner**, write a line in **Journal**, and log how you're feeling in **Mood**
4. Check **Statistics** to see it all summarized

---

## Design Decisions

A few deliberate simplifications, made with a portfolio project's scope in mind:

- **`db.create_all()` instead of migrations** — appropriate for SQLite at this scale; a production version would use Flask-Migrate/Alembic.
- **Mood is one entry per day (upsert)** rather than an open log — mood tracking works best as a daily check-in, and it keeps trend data in Statistics clean.
- **Task completion trend uses `updated_at`** as a proxy for "completed on this date," since there's no dedicated `completed_at` column — documented in `app/routes/stats.py`.
- **No CSRF protection yet** — flagged as a known gap; see Roadmap.
- **404 (not 403) on cross-user access** — if a user requests another user's task/entry by ID, the app returns a plain 404 rather than confirming the record exists under a 403, which would leak information.
- **Cross-platform date formatting** — templates use `%d` (not the Linux/macOS-only `%-d`) so the app runs identically on Windows, macOS, and Linux without `strftime` crashes.
- **SQLite path built with forward slashes** (`pathlib.Path(...).as_posix()`) rather than `os.path.join()`, since a raw Windows path with backslashes isn't a valid `sqlite:///` URI.

## License

This project is licensed under the [MIT License](LICENSE).
