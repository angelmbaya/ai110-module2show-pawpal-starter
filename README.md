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

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Schedule._sort_key`, `Schedule.generate`, `Schedule.sort_by_time` | Tasks are ordered by priority (high→low), then shorter duration, then non-recurring first. `sort_by_time()` returns the chronological plan.
| Filtering | `Schedule.generate(status_filter=...)`, `Schedule.filter_tasks` | Filter by task status (`pending`, `scheduled`, `completed`, `skipped`) or by pet name before or after generation.
| Conflict handling | `Schedule._has_conflict`, `Schedule.detect_conflicts` | Lightweight conflict detection collects warnings for overlaps or identical start times for the same pet. The scheduler returns warnings instead of raising exceptions.
| Recurring tasks | `Task.recurring`, `Owner.complete_task` | When a recurring task is completed, a fresh pending instance for the next occurrence is automatically created and added to the pet.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
