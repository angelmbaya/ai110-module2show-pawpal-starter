# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- The system should be able to add a pet's details, add/edit tasks, and generate a working and editable schedule.

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

For my initial PawPal+ design, I chose four main classes: Task, Pet, Owner, and Schedule.

The Task class represents one pet care responsibility, such as feeding, walking, medication, or grooming. It stores the task’s name, duration, priority, whether it repeats, and how often it repeats. Its main responsibility is to describe what needs to be done and check whether it can fit into a certain amount of available time.

The Pet class represents an individual pet in the system. It stores the pet’s basic details, including name, species, breed, and age. It also keeps a list of tasks connected to that specific pet. Its main responsibility is to manage a pet’s care tasks by adding or removing them.

The Owner class represents the person using PawPal+. It stores the owner’s name, available care time, preferences, and list of pets. Its responsibility is to manage the pets registered to that owner and help define the constraints the schedule must follow.

The Schedule class is responsible for creating the daily care plan. It stores the day, planned tasks, total time used, and an explanation of the schedule. Its main responsibility is to sort tasks by priority, choose tasks that fit within the owner’s available time, and explain why that schedule was created.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. After reviewing my initial skeleton, I made four design changes:

1. **Priority became an enum instead of a free-form string.** Originally `priority` was a plain string like `"high"`/`"medium"`/`"low"`. A typo such as `"hi"` would have sorted incorrectly with no error, and sorting required mapping strings to numbers. I replaced it with a `Priority(IntEnum)` (LOW=1, MEDIUM=2, HIGH=3) so tasks sort directly by their value, invalid priorities are impossible, and the UI gets a fixed set of choices.

2. **Schedule is now linked to the Owner.** My first version had `Schedule` take only a `day`, which meant the caller had to manually gather every pet's tasks and the owner's time budget and pass them in. This contradicted my UML's "Owner generates Schedule" relationship. I gave `Schedule` an `owner` reference and added an `Owner.generate_schedule()` method so the owner drives plan creation and the schedule can read `available_minutes` and `pets` itself.

3. **Added a PlannedItem class with start times.** The schedule originally stored a flat `list[Task]`, which lost track of which pet each task belonged to and had no time-of-day. Since the target output shows scheduled times (e.g. "08:00 — Morning walk") and supports multiple pets, I introduced `PlannedItem(pet, task, start_time)` and changed the schedule to hold `list[PlannedItem]`. This makes per-pet labels and time-slot/conflict handling possible.

4. **Made sorting an internal helper.** `sort_by_priority` was public, which invited callers to sort separately from `generate` and risk inconsistent ordering. I renamed it to `_sort_by_priority` so sorting stays an internal step of `generate`, and decided the tie-break rule up front (same priority → shorter duration first, to fit more tasks).

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
