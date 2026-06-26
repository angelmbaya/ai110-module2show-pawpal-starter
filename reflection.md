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

1. Priority became an enum instead of a free-form string. Originally priority was a plain string like "high"/"medium"/"low". A typo such as "hi" would have sorted incorrectly with no error, and sorting required mapping strings to numbers. I replaced it with a Priority(IntEnum) (LOW=1, MEDIUM=2, HIGH=3) so tasks sort directly by their value, invalid priorities are impossible, and the UI gets a fixed set of choices.

2. Schedule is now linked to the Owner. My first version had Schedule take only a day, which meant the caller had to manually gather every pet's tasks and the owner's time budget and pass them in. This contradicted my UML's "Owner generates Schedule" relationship. I gave Schedule an owner reference and added an Owner.generate_schedule() method so the owner drives plan creation and the schedule can read available_minutes and pets itself.

3. Added a PlannedItem class with start times. The schedule originally stored a flat list[Task], which lost track of which pet each task belonged to and had no time-of-day. Since the target output shows scheduled times (e.g. "08:00 — Morning walk") and supports multiple pets, I introduced PlannedItem(pet, task, start_time) and changed the schedule to hold list[PlannedItem]. This makes per-pet labels and time-slot/conflict handling possible.

4. Made sorting an internal helper. sort_by_priority was public, which invited callers to sort separately from generate and risk inconsistent ordering. I renamed it to _sort_by_priority so sorting stays an internal step of generate, and decided the tie-break rule up front (same priority → shorter duration first, to fit more tasks).

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
The scheduler considers the following constraints:

- Owner available time (`available_minutes`) — the hard budget for the day's plan.
- Task priority (`Priority` enum) — higher priority tasks are preferred.
- Task duration — shorter tasks are favored when priorities are equal so more items fit.
- Recurrence — recurring tasks are re-created after completion and remain eligible for scheduling.

Prioritization is purposely simple and greedy: rank by priority, tie-break by duration, and prefer non-recurring tasks. This reflects the common user need to fit more high-priority items into a limited morning routine; it keeps the algorithm fast and predictable.
**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

One concrete tradeoff the scheduler makes is to prefer higher-priority, shorter-duration tasks over lower-priority longer tasks (priority → duration as a tie-break). This greedy strategy helps maximize the number of tasks completed within a limited time budget, which is often what a busy owner wants: fit more essential items into the morning. The downside is that it can unfairly starve a single longer task of time even if that longer task is important for a particular pet (for example, a long grooming session that must happen once). A more optimal but more complex approach (like knapsack-style dynamic programming or backtracking search) could yield globally better allocations but would increase implementation complexity and runtime; for a responsive UI and simple daily planning needs the greedy rule is a reasonable compromise.

I used AI iteratively across the project for design refinement, implementation suggestions, targeted refactorings, and test generation. The most effective prompts were concise requests for one focused change (for example: "add conflict detection to Schedule" or "return planned items sorted by start time and display as a table in Streamlit"). Asking for small, testable edits and for tests to validate behavior produced the best results.

**b. Judgment and verification**

- I evaluated AI suggestions by running the test suite and manually running `main.py` to inspect outputs. When the AI suggested code that would change public APIs (like method names), I favored minimal, backwards-compatible changes and added small tests to validate behavior.
- I rejected or modified suggestions that introduced unnecessary complexity without clear benefit (for example, premature attempts to implement a full optimal knapsack solver). Instead I accepted a greedy heuristic and documented the tradeoff.

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
I am most satisfied with producing a working, test-covered scheduler that integrates cleanly with a simple Streamlit UI and that handles recurring tasks and conflict warnings gracefully. The small test suite gives confidence that key behaviors (sorting, recurrence, conflicts) work as intended.

**b. What you would improve**

- Replace the greedy scheduler with a lightweight optimization (e.g., bounded knapsack or integer programming) to better handle long, high-value tasks.
- Add persistence (a lightweight JSON or SQLite store) so owners' pets and tasks survive restarts and can be edited through the UI.

**c. Key takeaway**

- Acting as the lead architect when collaborating with AI means keeping control of the high-level design, asking for incremental changes, and verifying behavior with small unit tests. AI accelerates iteration, but you must still set constraints and make tradeoffs explicit.

**d. Which AI features were most effective?**

- Focused code edits and diffs: asking for patches that modify specific functions or add small helper methods worked especially well and reduced the need for manual merges.
- Test generation: having the AI propose small unit tests for edge cases (sorting, recurrence, conflict) made verification fast and guided design.
- Refactoring suggestions: the AI helped simplify sorting logic and add clear docstrings that improved readability.

**e. How separate chat sessions helped organization**

- Using separate sessions for design, implementation, and testing created clear mental checkpoints. Each session had a focused goal (UML → code skeletons → feature implementation → tests → docs), which reduced context switching and made it easier to roll back or rework specific areas without losing the overall picture.

**f. What I learned about being a lead architect with AI collaboration**

- Maintain a small, testable scope for each change. Request small, verifiable patches from the AI, run tests, and iterate.
- Be explicit about invariants and user-facing APIs so the AI can make safe edits.
- Use the AI to explore alternatives quickly, but retain final authority to choose tradeoffs; document those tradeoffs clearly for future maintainers.
**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
