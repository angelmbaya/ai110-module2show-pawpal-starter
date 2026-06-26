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
