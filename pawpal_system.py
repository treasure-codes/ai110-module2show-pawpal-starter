"""
PawPal+ — Core System
Tracks pet care tasks (feeding, walks, medications, appointments)
with sorting, filtering, recurrence, and conflict detection.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


# ──────────────────────────────────────────────
# Task
# ──────────────────────────────────────────────

@dataclass
class Task:
    """A single care task for a pet."""

    description: str
    time: str                        # "HH:MM" (24-hour)
    frequency: Optional[str] = None  # None | "Daily" | "Weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> Optional[datetime]:
        """Return the next scheduled datetime if the task recurs."""
        if self.frequency is None:
            return None
        now = datetime.now()
        task_time = datetime.strptime(self.time, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        if self.frequency == "Daily":
            return task_time + timedelta(days=1)
        if self.frequency == "Weekly":
            return task_time + timedelta(weeks=1)
        return None

    def __str__(self) -> str:
        status = "X" if self.completed else "o"
        freq = f" [{self.frequency}]" if self.frequency else ""
        return f"[{status}] {self.time}  {self.description}{freq}"


# ──────────────────────────────────────────────
# Pet
# ──────────────────────────────────────────────

@dataclass
class Pet:
    """A pet belonging to an owner."""

    name: str
    species: str = "dog"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def __str__(self) -> str:
        return f"{self.name} ({self.species})"


# ──────────────────────────────────────────────
# Owner
# ──────────────────────────────────────────────

@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


# ──────────────────────────────────────────────
# Scheduler
# ──────────────────────────────────────────────

class Scheduler:
    """Manages and analyses tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Delegate to owner to retrieve all (pet, task) pairs."""
        return self.owner.get_all_tasks()

    def sort_by_time(self) -> list[tuple[Pet, Task]]:
        """Return all tasks sorted chronologically by time string."""
        return sorted(
            self.get_all_tasks(),
            key=lambda pair: datetime.strptime(pair[1].time, "%H:%M")
        )

    def filter_tasks(
        self,
        keyword: str = "",
        completed: Optional[bool] = None,
        pet_name: str = "",
    ) -> list[tuple[Pet, Task]]:
        """
        Filter tasks by optional keyword (description), completion status,
        and/or pet name (case-insensitive).
        """
        results = self.get_all_tasks()

        if keyword:
            kw = keyword.lower()
            results = [(p, t) for p, t in results if kw in t.description.lower()]

        if completed is not None:
            results = [(p, t) for p, t in results if t.completed == completed]

        if pet_name:
            pn = pet_name.lower()
            results = [(p, t) for p, t in results if p.name.lower() == pn]

        return results

    def detect_conflicts(self, window_minutes: int = 10) -> list[tuple[Task, Task]]:
        """
        Return pairs of tasks scheduled within `window_minutes` of each other.
        Useful for spotting overlapping or back-to-back care tasks.
        """
        sorted_tasks = self.sort_by_time()
        conflicts: list[tuple[Task, Task]] = []

        for i in range(len(sorted_tasks) - 1):
            _, task_a = sorted_tasks[i]
            _, task_b = sorted_tasks[i + 1]

            time_a = datetime.strptime(task_a.time, "%H:%M")
            time_b = datetime.strptime(task_b.time, "%H:%M")
            delta = abs((time_b - time_a).total_seconds() / 60)

            if delta <= window_minutes:
                conflicts.append((task_a, task_b))

        return conflicts

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """
        Mark a task complete. If it recurs, create and attach the next
        occurrence to the same pet and return it; otherwise return None.
        """
        task.mark_complete()

        if task.frequency is None:
            return None

        # Find which pet owns this task
        owner_pet: Optional[Pet] = None
        for pet, t in self.get_all_tasks():
            if t is task:
                owner_pet = pet
                break

        if owner_pet is None:
            return None

        next_dt = task.next_occurrence()
        if next_dt is None:
            return None

        new_task = Task(
            description=task.description,
            time=next_dt.strftime("%H:%M"),
            frequency=task.frequency,
            completed=False,
        )
        owner_pet.add_task(new_task)
        return new_task

    def print_schedule(self) -> None:
        """Print a formatted, time-sorted schedule for all pets."""
        sorted_tasks = self.sort_by_time()
        line = "-" * 40
        print(f"\n{line}")
        print(f"  Schedule for {self.owner.name}'s pets")
        print(line)

        if not sorted_tasks:
            print("  No tasks scheduled.")
        else:
            for pet, task in sorted_tasks:
                print(f"  {task}  <- {pet.name}")

        print(f"{line}\n")
