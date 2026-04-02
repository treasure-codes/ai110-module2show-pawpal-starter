# PawPal+

A pet care scheduling assistant built with Python and Streamlit.

PawPal+ helps busy pet owners stay on top of daily care routines — walks, feedings, medications, and appointments — across multiple pets. It detects scheduling conflicts, supports recurring tasks, and provides a clean, interactive schedule view.

---

## Features

| Feature | Description |
|---|---|
| **Task tracking** | Add feeding, walk, medication, and appointment tasks per pet |
| **Sorting** | All tasks displayed in chronological order across all pets |
| **Filtering** | Filter by keyword, pet name, or completion status |
| **Recurring tasks** | Mark a Daily or Weekly task complete and the next occurrence is auto-created |
| **Conflict detection** | Tasks scheduled within 10 minutes of each other trigger a warning |

---

## How to Run

### Setup

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the demo script

```bash
python main.py
```

Prints a formatted schedule to the terminal, demonstrates conflict detection, filtering, and recurring task completion.

### Run the Streamlit UI

```bash
streamlit run app.py
```

Opens an interactive browser app where you can add pets and tasks, view the schedule, detect conflicts, and mark tasks complete.

### Run the tests

```bash
python -m pytest tests/ -v
```

All 12 tests should pass.

---

## Project Structure

```
pawpal_system.py       # Core classes: Task, Pet, Owner, Scheduler
main.py                # Terminal demo script
app.py                 # Streamlit UI
tests/
  test_pawpal.py       # pytest test suite (12 tests)
reflection.md          # Design and AI collaboration reflection
```

---

## Smarter Scheduling

The `Scheduler` class sits on top of the `Owner` model and provides four core capabilities:

- **`sort_by_time()`** — uses `sorted()` with a lambda that parses `"HH:MM"` strings into `datetime` objects for correct ordering
- **`filter_tasks(keyword, completed, pet_name)`** — composable, all arguments optional
- **`detect_conflicts(window_minutes=10)`** — scans adjacent sorted tasks for time proximity; the window is configurable
- **`mark_task_complete(task)`** — completes the task and, if it recurs (`Daily` or `Weekly`), clones it with the next scheduled time using `datetime + timedelta`

The scheduler does not manage task duration or priority ranking — it operates purely on scheduled times. This keeps the logic simple and transparent.

---

## Testing PawPal+

Tests are organized into five focused classes in `tests/test_pawpal.py`:

| Test Class | What it covers |
|---|---|
| `TestTaskCompletion` | `mark_complete()` sets flag; idempotent on repeated calls |
| `TestAddTaskToPet` | Single and multiple task attachment |
| `TestSorting` | Chronological order, cross-pet sorting |
| `TestRecurringTask` | Daily/Weekly creates next occurrence; one-time returns `None` |
| `TestConflictDetection` | Detects close tasks; respects configurable window; no false positives |

---

## Confidence Level

**★★★★☆**

Core scheduling logic (sorting, filtering, recurrence, conflict detection) is fully tested and working. The main limitation is that conflict detection only checks time proximity between adjacent tasks — it does not account for task duration or multi-pet resource contention. Given more time, adding duration-aware overlap detection and priority-based scheduling would be the next improvements.
