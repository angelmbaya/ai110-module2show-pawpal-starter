"""PawPal+ system skeleton.

Class stubs generated from diagrams/uml.mmd. Logic is intentionally left
unimplemented (raises NotImplementedError) so it can be filled in incrementally.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    """A single pet care task (walk, feeding, meds, etc.)."""

    name: str
    duration: int  # minutes
    priority: str = "medium"  # e.g. "high" | "medium" | "low"
    recurring: bool = False
    frequency: str = ""  # e.g. "daily" | "weekly"

    def fits_within(self, minutes: int) -> bool:
        """Return True if this task can fit in the given number of minutes."""
        raise NotImplementedError


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
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        raise NotImplementedError


@dataclass
class Owner:
    """The pet owner and their care constraints."""

    name: str
    available_minutes: int = 0
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        raise NotImplementedError

    def remove_pet(self, pet: Pet) -> None:
        """Unregister a pet from this owner."""
        raise NotImplementedError


class Schedule:
    """Builds and explains a daily care plan given tasks and time constraints."""

    def __init__(self, day: date | None = None) -> None:
        self.day: date | None = day
        self.planned_tasks: list[Task] = []
        self.total_minutes: int = 0
        self.explanation: str = ""

    def generate(self, tasks: list[Task], available_minutes: int) -> list[Task]:
        """Select tasks that fit within available_minutes, ordered by priority."""
        raise NotImplementedError

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted highest priority first."""
        raise NotImplementedError

    def explain(self) -> str:
        """Return a human-readable explanation of why this plan was chosen."""
        raise NotImplementedError
