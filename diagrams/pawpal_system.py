"""PawPal+ system implementation.

Models a pet owner, their pets, the care tasks each pet needs, and a Schedule
that builds a daily plan: it sorts tasks by priority, greedily selects the ones
that fit the owner's available time, assigns each a start time, and explains why.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import IntEnum


TASK_STATUSES = ("pending", "scheduled", "completed", "skipped")


class Priority(IntEnum):
    """Task priority. Higher value = scheduled first."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


# When the care day starts. Tasks are scheduled back-to-back from here.
DAY_START = time(8, 0)


@dataclass
class Task:
    """A single pet care task (walk, feeding, meds, etc.)."""

    name: str
    duration: int  # minutes
    priority: Priority = Priority.MEDIUM
    recurring: bool = False
    frequency: str = ""  # e.g. "daily" | "weekly"
    status: str = TASK_STATUSES[0]

    def __post_init__(self) -> None:
        """Validate duration and coerce priority to the Priority enum."""
        if self.duration <= 0:
            raise ValueError(f"Task '{self.name}' duration must be positive.")
        # Allow callers to pass a plain int/str; coerce to the enum.
        self.priority = Priority(self.priority)
        if self.status not in TASK_STATUSES:
            raise ValueError(
                f"Task '{self.name}' status must be one of {TASK_STATUSES}, got {self.status!r}."
            )
        if self.recurring and not self.frequency:
            self.frequency = "daily"

    def fits_within(self, minutes: int) -> bool:
        """Return True if this task can fit in the given number of minutes."""
        return self.duration <= minutes

    def mark_scheduled(self) -> None:
        """Mark this task as scheduled for the current planning run."""
        self.status = "scheduled"

    def mark_skipped(self) -> None:
        """Mark this task as skipped because there was not enough time."""
        if self.status != "completed":
            self.status = "skipped"

    def mark_completed(self) -> None:
        """Mark this task completed and exclude it from future schedules."""
        self.status = "completed"

    def due_for_schedule(self) -> bool:
        """Return True if this task should be considered during schedule generation."""
        return self.status == "pending" or self.recurring

    @property
    def is_recurring(self) -> bool:
        return self.recurring


@dataclass
class Pet:
    """A pet that care tasks are planned for."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet and avoid duplicate task names."""
        normalized_name = task.name.strip().lower()
        if not any(existing.name.strip().lower() == normalized_name for existing in self.tasks):
            self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet (no-op if not present)."""
        if task in self.tasks:
            self.tasks.remove(task)

    def pending_tasks(self) -> list[Task]:
        """Return tasks that are pending and available for scheduling."""
        return [task for task in self.tasks if task.status == "pending"]

    def completed_tasks(self) -> list[Task]:
        return [task for task in self.tasks if task.status == "completed"]


@dataclass
class Owner:
    """The pet owner and their care constraints."""

    name: str
    available_minutes: int = 0
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner, preventing duplicates by name."""
        normalized_name = pet.name.strip().lower()
        if not any(existing.name.strip().lower() == normalized_name for existing in self.pets):
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Unregister a pet from this owner (no-op if not present)."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Find a pet by name."""
        normalized = name.strip().lower()
        for pet in self.pets:
            if pet.name.strip().lower() == normalized:
                return pet
        return None

    def complete_task(self, pet: Pet, task: Task) -> Task | None:
        """Mark a task as completed for a given pet.

        If the task is recurring (daily/weekly), create and add a fresh pending
        instance of the same task to the pet for the next occurrence.

        Returns the new Task instance when one is created, otherwise None.
        """
        if task not in pet.tasks:
            return None

        task.mark_completed()
        if task.recurring:
            new_task = Task(
                name=task.name,
                duration=task.duration,
                priority=task.priority,
                recurring=task.recurring,
                frequency=task.frequency,
            )
            pet.add_task(new_task)
            return new_task
        return None

    def generate_schedule(
        self,
        day: date | None = None,
        pet_name: str | None = None,
        status_filter: str = "pending",
    ) -> "Schedule":
        """Build a daily plan for this owner across matching pets and task statuses."""
        schedule = Schedule(owner=self, day=day)
        schedule.generate(pet_name=pet_name, status_filter=status_filter)
        return schedule


@dataclass
class PlannedItem:
    """One scheduled task: which pet, which task, and when it starts."""

    pet: Pet
    task: Task
    start_time: time | None = None


class Schedule:
    """Builds and explains a daily care plan given an owner's tasks and time budget."""

    def __init__(self, owner: Owner, day: date | None = None) -> None:
        """Initialize an empty plan bound to an owner and an optional day."""
        self.owner: Owner = owner
        self.day: date | None = day
        self.planned_items: list[PlannedItem] = []
        self.total_minutes: int = 0
        self.explanation: str = ""
        # Non-fatal runtime warnings discovered during planning (conflicts, overlaps)
        self.warnings: list[str] = []
        # Tasks considered but dropped because time ran out, for the explanation.
        self.skipped: list[tuple[Pet, Task]] = []

    def generate(
        self,
        pet_name: str | None = None,
        status_filter: str = "pending",
    ) -> list[PlannedItem]:
        """Plan the priority-ordered tasks that fit the owner's time, with start times."""
        if status_filter not in TASK_STATUSES:
            raise ValueError(
                f"status_filter must be one of {TASK_STATUSES}, got {status_filter!r}."
            )

        self.planned_items = []
        self.skipped = []
        self.total_minutes = 0

        pets = self.owner.pets
        if pet_name:
            pet = self.owner.get_pet(pet_name)
            pets = [pet] if pet else []

        task_pairs = []
        for pet in pets:
            for task in pet.tasks:
                if status_filter == "pending":
                    if not task.due_for_schedule():
                        continue
                elif task.status != status_filter:
                    continue
                task_pairs.append((pet, task))

        task_pairs.sort(key=lambda pair: self._sort_key(pair[1]))

        remaining = self.owner.available_minutes
        cursor = datetime.combine(self.day or date.today(), DAY_START)

        for pet, task in task_pairs:
            if task.fits_within(remaining):
                start_time = cursor
                end_time = cursor + timedelta(minutes=task.duration)
                if self._has_conflict(start_time, end_time):
                    task.mark_skipped()
                    self.skipped.append((pet, task))
                    continue

                self.planned_items.append(
                    PlannedItem(pet=pet, task=task, start_time=cursor.time())
                )
                task.mark_scheduled()
                remaining -= task.duration
                self.total_minutes += task.duration
                cursor = end_time
            else:
                task.mark_skipped()
                self.skipped.append((pet, task))

        self.explanation = self.explain()
        return self.planned_items

    def sort_by_time(self) -> list[PlannedItem]:
        """Return planned items sorted by their scheduled start time.

        Useful for presenting the final plan in chronological order. Items with
        no start time are placed at the end.
        """
        return sorted(
            self.planned_items,
            key=lambda item: item.start_time if item.start_time is not None else time.max,
        )

    def filter_tasks(self, pet_name: str | None = None, status: str | None = None) -> list[PlannedItem]:
        """Return planned items filtered by pet name and/or task status.

        - `pet_name`: case-insensitive pet name to keep (None for all pets)
        - `status`: one of TASK_STATUSES to filter by (None for any status)
        """
        results: list[PlannedItem] = []
        for item in self.planned_items:
            if pet_name and item.pet.name.strip().lower() != pet_name.strip().lower():
                continue
            if status and item.task.status != status:
                continue
            results.append(item)
        return results

    def detect_conflicts(self) -> list[str]:
        """Detect lightweight conflicts among already planned items.

        Returns a list of human-readable warning messages for any overlapping
        tasks or two tasks scheduled at the same start time for the same pet.
        This method does not raise — it collects warnings so the caller can
        present them to the user.
        """
        warnings: list[str] = []
        n = len(self.planned_items)
        for i in range(n):
            a = self.planned_items[i]
            a_start = datetime.combine(self.day or date.today(), a.start_time)
            a_end = a_start + timedelta(minutes=a.task.duration)
            for j in range(i + 1, n):
                b = self.planned_items[j]
                b_start = datetime.combine(self.day or date.today(), b.start_time)
                b_end = b_start + timedelta(minutes=b.task.duration)

                # Same pet and identical start time
                if a.pet == b.pet and a.start_time == b.start_time:
                    msg = (
                        f"Warning: {a.pet.name} has two tasks at {a.start_time.strftime('%H:%M')}: "
                        f"'{a.task.name}' and '{b.task.name}'."
                    )
                    warnings.append(msg)
                    continue

                # Overlap detection (any intersection)
                if a_start < b_end and b_start < a_end:
                    msg = (
                        f"Warning: task overlap between {a.pet.name}: '{a.task.name}' "
                        f"({a_start.time().strftime('%H:%M')}-{a_end.time().strftime('%H:%M')}) and "
                        f"'{b.task.name}' ({b_start.time().strftime('%H:%M')}-{b_end.time().strftime('%H:%M')})."
                    )
                    warnings.append(msg)

        # Deduplicate and store on the schedule object for convenience
        unique = []
        for w in warnings:
            if w not in unique:
                unique.append(w)
        self.warnings = unique
        return self.warnings

    def _has_conflict(self, start: datetime, end: datetime) -> bool:
        """Return True if the new task overlaps an already scheduled interval."""
        for item in self.planned_items:
            item_start = datetime.combine(self.day or date.today(), item.start_time)
            item_end = item_start + timedelta(minutes=item.task.duration)
            if start < item_end and end > item_start:
                return True
        return False

    @staticmethod
    def _sort_key(task: Task) -> tuple[int, int, int]:
        """Compute a stable sort key for tasks.

        Sort order (highest precedence first):
        1. priority (higher first)
        2. shorter duration (so we can fit more tasks)
        3. non-recurring tasks before recurring (prefer one-off work)

        Returns a tuple suitable for use with Python's sorted().
        """
        priority_key = -int(task.priority)
        duration_key = task.duration
        recurring_key = 0 if not task.recurring else 1
        return (priority_key, duration_key, recurring_key)

    def explain(self) -> str:
        """Return a human-readable explanation of why this plan was chosen."""
        if not self.owner.pets or not any(pet.tasks for pet in self.owner.pets):
            return "No tasks to schedule."

        lines = [
            f"Planned {len(self.planned_items)} task(s) using "
            f"{self.total_minutes} of {self.owner.available_minutes} available minutes, "
            f"ordered by priority (highest first)."
        ]
        for item in self.planned_items:
            start = item.start_time.strftime("%H:%M") if item.start_time else "--:--"
            lines.append(
                f"  {start} — {item.task.name} ({item.task.duration} min) "
                f"[priority: {item.task.priority.name.lower()}] for {item.pet.name}"
            )
        for pet, task in self.skipped:
            lines.append(
                f"  Skipped: {task.name} ({task.duration} min) for {pet.name} "
                f"— not enough time remaining."
            )
        return "\n".join(lines)
