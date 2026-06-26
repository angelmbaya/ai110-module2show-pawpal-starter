import streamlit as st
from diagrams.pawpal_system import Owner, Pet, Task, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
PawPal+ connects a pet owner, pets, and care tasks to the scheduler defined in
`diagrams/pawpal_system.py`.
"""
)

if "owner" not in st.session_state or st.session_state.owner is None:
    st.session_state.owner = Owner(name="Jordan", available_minutes=120)

owner: Owner = st.session_state.owner

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value=owner.name)
available_minutes = st.number_input(
    "Available minutes",
    min_value=0,
    max_value=1440,
    value=owner.available_minutes,
)

owner.name = owner_name
owner.available_minutes = available_minutes

st.divider()

st.subheader("Add a pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
breed = st.text_input("Breed", value="")
age = st.number_input("Age", min_value=0, max_value=50, value=0)

if st.button("Add pet"):
    if pet_name.strip():
        pet = Pet(name=pet_name.strip(), species=species, breed=breed.strip(), age=age)
        owner.add_pet(pet)
        st.success(f"Added pet {pet.name} to owner {owner.name}.")
    else:
        st.error("Please give the pet a name before adding.")

if owner.pets:
    st.markdown("### Current pets")
    for pet in owner.pets:
        st.write(f"- {pet.name} ({pet.species})")
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Add a task")
if owner.pets:
    pet_selection = st.selectbox("Select pet", owner.pets, format_func=lambda pet: pet.name)
    task_title = st.text_input("Task title", value="Morning walk")
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    priority = st.selectbox("Priority", list(Priority), format_func=lambda p: p.name.lower(), index=2)
    recurring = st.checkbox("Recurring task")
    frequency = st.text_input("Frequency", value="daily" if recurring else "")

    if st.button("Add task to pet"):
        if task_title.strip():
            task = Task(
                name=task_title.strip(),
                duration=int(duration),
                priority=priority,
                recurring=recurring,
                frequency=frequency.strip(),
            )
            pet_selection.add_task(task)
            st.success(f"Added task '{task.name}' to {pet_selection.name}.")
        else:
            st.error("Please provide a task title.")

    if any(pet.tasks for pet in owner.pets):
        st.markdown("### Current pet tasks")
        for pet in owner.pets:
            if pet.tasks:
                st.write(f"**{pet.name}**")
                for task in pet.tasks:
                    st.write(f"- {task.name} ({task.duration} min, priority={task.priority.name.lower()})")
else:
    st.info("Add a pet first, then assign tasks to that pet.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate the actual schedule using Owner.generate_schedule().")

schedule_pet = st.selectbox(
    "Schedule pets",
    ["all"] + [pet.name for pet in owner.pets],
    index=0,
)
schedule_status = st.selectbox(
    "Task status",
    ["pending", "scheduled", "completed", "skipped"],
    index=0,
)

if st.button("Generate schedule"):
    if not owner.pets:
        st.warning("Add at least one pet before generating a schedule.")
    elif not any(pet.tasks for pet in owner.pets):
        st.warning("Add at least one task before generating a schedule.")
    else:
        pet_name = None if schedule_pet == "all" else schedule_pet
        schedule = owner.generate_schedule(pet_name=pet_name, status_filter=schedule_status)

        # Detect conflicts and show warnings
        warnings = schedule.detect_conflicts()
        if warnings:
            for w in warnings:
                st.warning(w)

        st.success("Schedule generated")
        st.markdown("### Schedule Explanation")
        st.text(schedule.explanation)

        # Present the planned items in a chronological table
        planned = schedule.sort_by_time()
        if planned:
            rows = []
            for item in planned:
                rows.append(
                    {
                        "start_time": item.start_time.strftime("%H:%M") if item.start_time else "--:--",
                        "pet": item.pet.name,
                        "task": item.task.name,
                        "duration_min": item.task.duration,
                        "priority": item.task.priority.name.lower(),
                        "status": item.task.status,
                    }
                )
            st.table(rows)
        else:
            st.info("No planned items to show.")

        if schedule.skipped:
            st.markdown("### Skipped tasks")
            skipped_rows = [
                {
                    "pet": pet.name,
                    "task": task.name,
                    "duration_min": task.duration,
                    "priority": task.priority.name.lower(),
                    "status": task.status,
                }
                for pet, task in schedule.skipped
            ]
            st.table(skipped_rows)
