# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

##Sample Output
Today's schedule for Sam:
Planned 5 task(s) using 85 of 90 available minutes, ordered by priority (highest first).
  08:00 — Feeding (10 min) [priority: high] for Biscuit
  08:10 — Feeding (10 min) [priority: high] for Whiskers
  08:20 — Morning walk (30 min) [priority: high] for Biscuit
  08:50 — Litter cleaning (15 min) [priority: medium] for Whiskers
  09:05 — Grooming (20 min) [priority: low] for Whiskers
  Skipped: Enrichment play (25 min) for Biscuit — not enough time remaining.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

Run the automated tests for PawPal+ with:

```bash
python -m pytest
```

What the tests cover:

- Core task behavior (adding tasks, status transitions).
- Scheduling correctness and ordering (priority then duration).
- Recurring task recreation when a recurring task is completed.
- Lightweight conflict detection for overlapping or same-time tasks.

Sample successful test run:

```bash
5 passed in 0.04s
```

Confidence in scheduler correctness based on these tests: ★★★★☆ (4/5)

## 📐 Smarter Scheduling

This project implements several practical scheduling behaviors to make daily pet care planning useful and predictable:

- Task ordering: tasks are ordered by `Priority` (HIGH → MEDIUM → LOW), then by shorter duration to fit more items into limited time, and non-recurring tasks are preferred over recurring ones when tie-breaking.
- Chronological view: `Schedule.sort_by_time()` produces the final ordered list of `PlannedItem`s with start times for display.
- Filtering: you can generate schedules for all pets or a single pet and filter tasks by status (`pending`, `scheduled`, `completed`, `skipped`) using `Schedule.generate(..., status_filter=...)` and `Schedule.filter_tasks(...)`.
- Recurring tasks: recurring tasks (daily/weekly) persist; when a recurring task is marked completed via `Owner.complete_task(...)`, the system creates a fresh pending instance for the next occurrence.
- Conflict detection: the scheduler uses a lightweight overlap detection and `Schedule.detect_conflicts()` to collect human-readable warnings when two tasks overlap or two tasks for the same pet share the same start time. Warnings are surfaced to the UI instead of raising errors.

Key methods and where to look in code:

- `Schedule.generate()` — core planning algorithm that selects tasks to fit available minutes.
- `Schedule._sort_key()` — stable sort key implementation (priority, duration, recurring).
- `Schedule.sort_by_time()`, `Schedule.filter_tasks()`, `Schedule.detect_conflicts()` — display & validation helpers.
- `Owner.complete_task()` — marks a task completed and recreates recurring tasks.


## 📸 Demo Walkthrough

The Streamlit UI (`app.py`) exposes the main features of PawPal+ for quick experimentation.

1. Owner panel: edit the owner name and available minutes. These values define the time budget used by the scheduler.
2. Add a pet: provide a pet name, species, breed and age. Pets are de-duplicated by name.
3. Add tasks to a pet: select a pet, enter a task title, duration, priority and whether it's recurring. Tasks are normalized to avoid duplicate names per pet.
4. Build schedule: choose which pet(s) to include (`all` or a single pet) and select a task status filter. Click `Generate schedule` to run the planner.
   - The app displays any detected conflicts as warnings using `st.warning`.
   - The schedule explanation is shown and the chronological plan is rendered as a table via `st.table`.
   - Skipped tasks (not enough time) are displayed in their own table.
5. Recurring tasks: when a recurring task is marked completed via code or future UI controls, the system automatically creates a fresh pending instance for the next occurrence.

Example workflow (user actions):

- Add owner "Jordan" with 120 available minutes.
- Add pet "Mochi" (dog) and pet "Biscuit" (dog).
- Add tasks: "Morning walk" (30, high) to Mochi, "Feeding" (10, high) to Biscuit, "Daily meds" (5, high, recurring) to Biscuit.
- Select `all` pets and `pending` tasks, then click `Generate schedule`.
- Inspect the chronological table, note any `st.warning` messages if conflicts are present, and view skipped tasks.

Sample CLI output from running `main.py` (example):

```bash
Today's schedule for Sam:
Planned 4 task(s) using 65 of 90 available minutes, ordered by priority (highest first).
  08:00 — Feeding (10 min) [priority: high] for Biscuit
  08:10 — Morning walk (30 min) [priority: high] for Biscuit
  08:40 — Litter cleaning (15 min) [priority: medium] for Whiskers
  08:55 — Grooming (10 min) [priority: low] for Whiskers
Warning: Biscuit has two tasks at 08:10: 'Morning walk' and 'Conflicting task'.
```
