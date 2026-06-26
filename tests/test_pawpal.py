"""Tests for core PawPal+ behaviors."""

from diagrams.pawpal_system import Owner, Pet, Task, Priority


def test_task_addition():
    """Adding a task to a pet stores it on the pet's task list."""
    pet = Pet(name="Biscuit", species="Dog")
    task = Task("Morning walk", duration=30, priority=Priority.HIGH)

    pet.add_task(task)

    assert task in pet.tasks
    assert len(pet.tasks) == 1


def test_task_completion():
    """A task that fits the time budget is included in the generated schedule."""
    owner = Owner(name="Sam", available_minutes=60)
    pet = Pet(name="Biscuit", species="Dog")
    task = Task("Feeding", duration=10, priority=Priority.HIGH)
    pet.add_task(task)
    owner.add_pet(pet)

    schedule = owner.generate_schedule()

    planned_tasks = [item.task for item in schedule.planned_items]
    assert task in planned_tasks
    assert schedule.total_minutes == 10


def test_sorting_correctness():
    """Tasks should be ordered by priority (high->low) and shorter duration first."""
    pet = Pet(name="Biscuit", species="Dog")
    # Add out-of-order tasks
    pet.add_task(Task("A", duration=30, priority=Priority.HIGH))
    pet.add_task(Task("B", duration=10, priority=Priority.HIGH))
    pet.add_task(Task("C", duration=5, priority=Priority.MEDIUM))

    owner = Owner(name="Sam", available_minutes=100)
    owner.add_pet(pet)

    schedule = owner.generate_schedule()
    planned = [item.task.name for item in schedule.planned_items]
    assert planned == ["B", "A", "C"]


def test_recurring_recreation():
    """Completing a recurring task should produce a fresh pending instance."""
    owner = Owner(name="Sam", available_minutes=60)
    pet = Pet(name="Biscuit", species="Dog")
    task = Task("Daily meds", duration=5, priority=Priority.HIGH, recurring=True, frequency="daily")
    pet.add_task(task)
    owner.add_pet(pet)

    new_task = owner.complete_task(pet, task)
    assert task.status == "completed"
    assert new_task is not None
    assert any(t is new_task for t in pet.tasks)
    assert new_task.status == "pending"


def test_conflict_detection():
    """Scheduler should report conflicts when two tasks occur at the same time."""
    owner = Owner(name="Alex", available_minutes=60)
    pet = Pet(name="Spot", species="Dog")
    pet.add_task(Task("T1", duration=20, priority=Priority.HIGH))
    pet.add_task(Task("T2", duration=20, priority=Priority.MEDIUM))
    owner.add_pet(pet)

    schedule = owner.generate_schedule()
    # Force a conflict by duplicating an item at the same start time
    if schedule.planned_items:
        first = schedule.planned_items[0]
        conflict_task = Task("Conflict", duration=10, priority=Priority.LOW)
        from diagrams.pawpal_system import PlannedItem

        conflict_item = PlannedItem(pet=first.pet, task=conflict_task, start_time=first.start_time)
        schedule.planned_items.append(conflict_item)

    warnings = schedule.detect_conflicts()
    assert isinstance(warnings, list)
    assert any("Warning" in w for w in warnings)
