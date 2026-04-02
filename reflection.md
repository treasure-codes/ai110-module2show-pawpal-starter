# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial design identified four classes with clear, non-overlapping responsibilities:

- **`Task`** — a single care action with a description, scheduled time, optional recurrence, and completion state. Kept as a pure data container with one behavior method (`mark_complete`).
- **`Pet`** — owns a list of tasks and provides `add_task()`. Represents one animal with a name and species.
- **`Owner`** — holds a list of pets and provides `get_all_tasks()`, which flattens all (pet, task) pairs into a single iterable. Acts as the root of the data model.
- **`Scheduler`** — takes an Owner and provides all scheduling intelligence: sorting, filtering, conflict detection, and recurrence handling. Deliberately separated from the data classes so logic stays in one place.

The UML was drawn as a simple composition chain: `Scheduler → Owner → Pet → Task`.

**b. Design changes**

One meaningful change during implementation: `mark_task_complete()` was initially planned as a method on `Task` itself. It was moved to `Scheduler` because creating the next recurring occurrence requires knowing which `Pet` owns the task — information that `Task` alone doesn't have. Keeping that lookup in `Scheduler` preserved clean separation between data and behavior.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers one constraint: **scheduled time** (`"HH:MM"`). Tasks are sorted and compared by time only. This was chosen as the primary constraint because it is always present — every task must have a time, making it a reliable, universal key for ordering and conflict checking.

**b. Tradeoffs**

The conflict detector checks **time proximity between adjacent tasks**, not true duration-based overlap. Two tasks 8 minutes apart trigger a warning, but the system doesn't know how long each task takes — a 30-minute walk starting at 07:00 and a feeding at 07:20 would not be flagged even though they genuinely overlap.

This tradeoff is reasonable for this project scope: adding duration tracking would require another field on every task and a different conflict algorithm. The proximity window (default: 10 minutes) is configurable, which lets users tune sensitivity without changing code. For a real production system, duration-aware scheduling would be the right next step.

---

## 3. AI Collaboration

**a. How AI was used**

AI tools were used throughout the project:

- **Design phase** — brainstorming which classes were needed and what their responsibilities should be, and generating a Mermaid UML diagram from a plain-English description
- **Implementation** — generating boilerplate for `@dataclass` definitions and the `Scheduler` methods, then reviewing the logic before accepting it
- **Testing** — suggesting test cases for edge cases like idempotent completion and the configurable conflict window
- **UI integration** — structuring the Streamlit session state pattern and form layout

The most useful prompts were specific and incremental: "generate `sort_by_time()` using `sorted()` and a lambda" produced cleaner output than "write the whole Scheduler class."

**b. Judgment and verification**

The AI initially suggested implementing `mark_task_complete()` as a method directly on `Task`, with `Task` importing `datetime` and handling the recurrence logic itself. This was rejected because it would make `Task` responsible for knowing its own next occurrence *and* for attaching that occurrence to the right `Pet` — but `Task` has no reference to its parent `Pet`. Accepting that suggestion would have forced either a circular reference or a design violation.

The fix was to move recurrence handling into `Scheduler`, which already has access to all (pet, task) pairs and can perform the parent lookup cleanly. This was verified by tracing through the data model before writing any code.

---

## 4. Testing and Verification

**a. What was tested**

The 12 tests cover the five most important behaviors:

1. Task completion sets the flag and is idempotent
2. Tasks attach correctly to pets
3. Sorting produces chronological order across multiple pets
4. Recurring tasks create a next occurrence; one-time tasks do not
5. Conflict detection fires for close tasks, respects the configurable window, and produces no false positives for well-spaced tasks

These were chosen because they represent the core promises of the system — if any of them break, the app is broken in a user-visible way.

**b. Confidence**

**★★★★☆** — High confidence in the tested behaviors. Edge cases not yet covered:

- Tasks scheduled exactly at midnight or spanning midnight
- Two tasks at the exact same time (zero-gap conflict)
- An owner with no pets calling `get_all_tasks()`
- Very large task lists (performance is untested)

---

## 5. Reflection

**a. What went well**

The clearest win was the separation between data (`Task`, `Pet`, `Owner`) and behavior (`Scheduler`). Every time a new feature was needed — filtering, recurrence, conflict detection — there was an obvious place to put it. No methods ended up in the wrong class.

**b. What would be improved**

The next iteration would add **task duration** as a first-class field on `Task`. This would unlock duration-aware conflict detection (true overlap, not just proximity) and eventually make it possible to generate a packed daily schedule that fits within an owner's available time windows.

**c. Key takeaway**

Designing the UML before writing code forced a decision that turned out to matter: where does recurrence logic live? The answer wasn't obvious from the requirements, but working through the class diagram made the right answer clear — behavior that needs cross-object access belongs in the orchestrating class (`Scheduler`), not in the data objects. That's a pattern that applies well beyond this project.

Working in separate, named steps (design → stubs → implementation → tests → UI) also made it easier to use AI effectively. Each step had a narrow, well-defined output, which meant AI suggestions were easier to evaluate and easier to reject when they didn't fit.
