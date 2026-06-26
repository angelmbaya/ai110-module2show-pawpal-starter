"""PawPal+ demo script.

Builds an owner with two pets and several care tasks, then prints today's
generated schedule to the terminal.
"""

from diagrams.pawpal_system import Owner, Pet, Task, Priority


def main() -> None:
    owner = Owner(name="Sam", available_minutes=90)

    # First pet and its tasks.
    biscuit = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=3)
    biscuit.add_task(Task("Morning walk", duration=30, priority=Priority.HIGH))
    biscuit.add_task(Task("Feeding", duration=10, priority=Priority.HIGH))
    biscuit.add_task(Task("Enrichment play", duration=25, priority=Priority.LOW))

    # Second pet and its tasks.
    whiskers = Pet(name="Whiskers", species="Cat", breed="Tabby", age=5)
    whiskers.add_task(Task("Feeding", duration=10, priority=Priority.HIGH))
    whiskers.add_task(Task("Litter cleaning", duration=15, priority=Priority.MEDIUM))
    whiskers.add_task(Task("Grooming", duration=20, priority=Priority.LOW))

    owner.add_pet(biscuit)
    owner.add_pet(whiskers)

    schedule = owner.generate_schedule()

    print(f"Today's schedule for {owner.name}:")
    print(schedule.explanation)


if __name__ == "__main__":
    main()
