# PawPal+ — Final UML Class Diagram

Paste the Mermaid code below into https://mermaid.live to export as PNG.

```mermaid
classDiagram
    class Task {
        +str description
        +str time
        +Optional~str~ frequency
        +bool completed
        +mark_complete()
        +next_occurrence() Optional~datetime~
        +__str__() str
    }

    class Pet {
        +str name
        +str species
        +list~Task~ tasks
        +add_task(task: Task)
        +__str__() str
    }

    class Owner {
        +str name
        +list~Pet~ pets
        +add_pet(pet: Pet)
        +get_all_tasks() list~tuple~
        +__str__() str
    }

    class Scheduler {
        +Owner owner
        +get_all_tasks() list~tuple~
        +sort_by_time() list~tuple~
        +filter_tasks(keyword, completed, pet_name) list~tuple~
        +detect_conflicts(window_minutes) list~tuple~
        +mark_task_complete(task) Optional~Task~
        +print_schedule()
    }

    Owner "1" --> "1..*" Pet : owns
    Pet  "1" --> "0..*" Task : has
    Scheduler "1" --> "1" Owner : manages
    Scheduler ..> Task : creates next occurrence
```

## Key design notes

- `Task` is a pure data object — it knows about itself but not its parent
- `Pet` is a container — no scheduling logic, only `add_task()`
- `Owner` is the data root — `get_all_tasks()` flattens all (pet, task) pairs
- `Scheduler` is the only class with cross-object logic; it holds a reference to `Owner` and navigates down to `Task`
- Recurrence: `Scheduler.mark_task_complete()` calls `Task.next_occurrence()` (datetime arithmetic) then attaches the new `Task` to the correct `Pet`
