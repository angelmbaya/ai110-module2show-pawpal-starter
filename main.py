"""PawPal+ demo script.

Builds an owner with two pets and several care tasks, then prints today's
generated schedule to the terminal.
"""

from diagrams.pawpal_system import Owner, Pet, Task, Priority, PlannedItem


def main() -> None:
    owner = Owner(name="Sam", available_minutes=90)

    # First pet with tasks added out of chronological order
    biscuit = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=3)
    # Intentionally adding tasks out of typical time order
    biscuit.add_task(Task("Feeding", duration=10, priority=Priority.HIGH))
    biscuit.add_task(Task("Enrichment play", duration=25, priority=Priority.LOW))
    biscuit.add_task(Task("Morning walk", duration=30, priority=Priority.HIGH))

    # Second pet
    whiskers = Pet(name="Whiskers", species="Cat", breed="Tabby", age=5)
    whiskers.add_task(Task("Feeding", duration=10, priority=Priority.HIGH))
    whiskers.add_task(Task("Litter cleaning", duration=15, priority=Priority.MEDIUM))

    owner.add_pet(biscuit)
    owner.add_pet(whiskers)

    # Generate and show schedule
    schedule = owner.generate_schedule()
    print(f"Today's schedule for {owner.name}:")
    print(schedule.explanation)

    # Show sorted by time (should be identical to printed schedule but demonstrates API)
    print("\nPlanned items (chronological):")
    for item in schedule.sort_by_time():
        print(f"- {item.start_time.strftime('%H:%M')} {item.pet.name}: {item.task.name}")

    # Filter tasks for a single pet
    print("\nFiltered (Biscuit):")
    for item in schedule.filter_tasks(pet_name="Biscuit"):
        print(f"- {item.start_time.strftime('%H:%M')} {item.pet.name}: {item.task.name} (status={item.task.status})")

    # Demonstrate recurring task recreation: mark a recurring task complete
    recurring = Task("Daily meds", duration=5, priority=Priority.HIGH, recurring=True, frequency="daily")
    biscuit.add_task(recurring)
    new = owner.complete_task(biscuit, recurring)
    print("\nAfter completing recurring task:")
    print(f"- Completed '{recurring.name}', created new instance: {new is not None}")

    # Simulate a conflict by manually inserting a planned item that shares a start time
    if schedule.planned_items:
        first = schedule.planned_items[0]
        # Create a conflicting planned item for the same pet at the same time
        conflict_task = Task("Conflicting task", duration=10, priority=Priority.MEDIUM)
        conflict_item = PlannedItem(pet=first.pet, task=conflict_task, start_time=first.start_time)
        schedule.planned_items.append(conflict_item)
        warnings = schedule.detect_conflicts()
        print("\nConflict detection output:")
        for w in warnings:
            print(w)


if __name__ == "__main__":
    main()
