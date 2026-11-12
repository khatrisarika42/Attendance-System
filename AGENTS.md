# AGENTS.md

Flask + SQLite attendance app (MVC). No README, no requirements.txt, no tests, no git repo.

## Running

```powershell
cd attendance_system
pip install flask          # not pinned anywhere; no requirements.txt exists
python app.py              # http://127.0.0.1:5000, debug=True, auto-reload
```

- **Run `app.py` from inside `attendance_system/`** — it imports `controllers.attendance_controller` and creates `database/attendance.db` via relative paths. Running from the repo root fails on import.
- `init_db()` runs at import time and creates the SQLite tables (`employees`, `attendance`) if missing; delete `attendance_system/database/attendance.db` to reset state.

## Generated code

- `generate_project.py` (repo root) is a generator that **rewrites every file in `attendance_system/` from hardcoded strings** in the script. Hand edits to the app are lost if it is re-run; keep `generate_project.py` and `attendance_system/` in sync when changing either.
- Running `generate_project.py` from inside `attendance_system/` instead of the repo root creates a nested `attendance_system/attendance_system/` duplicate — that nested copy currently exists and is stale/exact duplicate; do not edit it, edit only `attendance_system/`.

## Conventions that differ from Flask defaults

- Jinja templates live in `views/`, not `templates/` (`template_folder='views'` in `app.py`).
- Routes are on a Blueprint (`attendance_bp`) with `url_for('attendance.<endpoint>')`; HTML forms POST to plain paths (`/employees`, `/attendance`) and redirect after success (PRG pattern).
- Model functions in `models/attendance_model.py` open/close a raw `sqlite3` connection per call (rows accessed as dicts via `sqlite3.Row`); follow this pattern, no ORM.
- `app.secret_key` in `app.py` is required by Flask `flash()` — deleting it makes form submissions crash.
