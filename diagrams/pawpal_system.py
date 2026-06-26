"""PawPal+ system implementation.

Models a pet owner, their pets, the care tasks each pet needs, and a Schedule
that builds a daily plan: it sorts tasks by priority, greedily selects the ones
that fit the owner's available time, assigns each a start time, and explains why.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import IntEnum


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

    def __post_init__(self) -> None:
        """Validate duration and coerce priority to the Priority enum."""
        if self.duration <= 0:
            raise ValueError(f"Task '{self.name}' duration must be positive.")
        # Allow callers to pass a plain int/str; coerce to the enum.
        self.priority = Priority(self.priority)

    def fits_within(self, minutes: int) -> bool:
        """Return True if this task can fit in the given number of minutes."""
        return self.duration <= minutes


@dataclass
class Pet:
    """A pet that care tasks are planned for."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        if task not in self.tasks:
            self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet (no-op if not present)."""
        if task in self.tasks:
            self.tasks.remove(task)


@dataclass
class Owner:
    """The pet owner and their care constraints."""

    name: str
    available_minutes: int = 0
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Unregister a pet from this owner (no-op if not present)."""
        if pet in self.pets:
            self.pets.remove(pet)

    def generate_schedule(self, day: date | None = None) -> "Schedule":
        """Build a daily plan for this owner across all their pets."""
        schedule = Schedule(owner=self, day=day)
        schedule.generate()
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
        # Tasks considered but dropped because time ran out, for the explanation.
        self.skipped: list[tuple[Pet, Task]] = []

    def generate(self) -> list[PlannedItem]:
        """Plan the priority-ordered tasks that fit the owner's time, with start times."""
        # Reset so generate() is idempotent if called more than once.
        self.planned_items = []
        self.skipped = []
        self.total_minutes = 0

        # Pair every task with the pet it belongs to, then sort by priority.
        pet_tasks = [(pet, task) for pet in self.owner.pets for task in pet.tasks]
        pet_tasks.sort(key=lambda pair: self._sort_key(pair[1]))

        remaining = self.owner.available_minutes
        cursor = datetime.combine(self.day or date.today(), DAY_START)

        for pet, task in pet_tasks:
            if task.fits_within(remaining):
                self.planned_items.append(
                    PlannedItem(pet=pet, task=task, start_time=cursor.time())
                )
                remaining -= task.duration
                self.total_minutes += task.duration
                cursor += timedelta(minutes=task.duration)
            else:
                self.skipped.append((pet, task))

        self.explanation = self.explain()
        return self.planned_items

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered highest priority first, shortest duration as tie-break."""
        return sorted(tasks, key=self._sort_key)

    @staticmethod
    def _sort_key(task: Task) -> tuple[int, int]:
        """Sort key: highest priority first, then shortest duration to fit more tasks."""
        return (-int(task.priority), task.duration)

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
