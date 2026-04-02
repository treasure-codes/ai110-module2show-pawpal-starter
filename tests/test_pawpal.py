"""
PawPal+ — pytest test suite
Run with:  pytest tests/
"""

import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


# ── Fixtures ──────────────────────────────────

@pytest.fixture
def simple_owner() -> Owner:
    """Owner with one pet and three tasks at distinct times."""
    owner = Owner(name="Jordan")
    dog = Pet(name="Mochi", species="dog")
    dog.add_task(Task("Morning walk",      time="07:00", frequency="Daily"))
    dog.add_task(Task("Lunch feeding",     time="12:00"))
    dog.add_task(Task("Evening walk",      time="18:00", frequency="Daily"))
    owner.add_pet(dog)
    return owner


@pytest.fixture
def scheduler(simple_owner: Owner) -> Scheduler:
    return Scheduler(simple_owner)


# ── Tests ─────────────────────────────────────

class TestTaskCompletion:
    def test_mark_complete_sets_flag(self):
        task = Task("Brush teeth", time="09:00")
        assert task.completed is False
        task.mark_complete()
        assert task.completed is True

    def test_mark_complete_is_idempotent(self):
        task = Task("Brush teeth", time="09:00")
        task.mark_complete()
        task.mark_complete()  # should not raise
        assert task.completed is True


class TestAddTaskToPet:
    def test_add_single_task(self):
        pet = Pet(name="Luna", species="cat")
        task = Task("Feed", time="08:00")
        pet.add_task(task)
        assert len(pet.tasks) == 1
        assert pet.tasks[0] is task

    def test_add_multiple_tasks(self):
        pet = Pet(name="Luna", species="cat")
        for i in range(3):
            pet.add_task(Task(f"Task {i}", time=f"0{i + 7}:00"))
        assert len(pet.tasks) == 3


class TestSorting:
    def test_sort_returns_chronological_order(self, scheduler: Scheduler):
        sorted_tasks = scheduler.sort_by_time()
        times = [t.time for _, t in sorted_tasks]
        assert times == sorted(times)

    def test_sort_handles_multiple_pets(self):
        owner = Owner("Sam")
        dog = Pet("Rex", "dog")
        cat = Pet("Miso", "cat")
        dog.add_task(Task("Walk",   time="10:00"))
        cat.add_task(Task("Feed",   time="07:00"))
        dog.add_task(Task("Dinner", time="18:00"))
        owner.add_pet(dog)
        owner.add_pet(cat)

        s = Scheduler(owner)
        times = [t.time for _, t in s.sort_by_time()]
        assert times == ["07:00", "10:00", "18:00"]


class TestRecurringTask:
    def test_daily_creates_next_occurrence(self, scheduler: Scheduler):
        pet = scheduler.owner.pets[0]
        task = pet.tasks[0]  # Morning walk — Daily
        original_count = len(pet.tasks)

        next_task = scheduler.mark_task_complete(task)

        assert task.completed is True
        assert next_task is not None
        assert next_task.frequency == "Daily"
        assert next_task.completed is False
        assert len(pet.tasks) == original_count + 1

    def test_non_recurring_returns_none(self, scheduler: Scheduler):
        pet = scheduler.owner.pets[0]
        task = pet.tasks[1]  # Lunch feeding — no frequency
        original_count = len(pet.tasks)

        result = scheduler.mark_task_complete(task)

        assert task.completed is True
        assert result is None
        assert len(pet.tasks) == original_count  # no new task added

    def test_weekly_creates_next_occurrence(self):
        owner = Owner("Alex")
        pet = Pet("Buddy", "dog")
        task = Task("Flea treatment", time="10:00", frequency="Weekly")
        pet.add_task(task)
        owner.add_pet(pet)

        s = Scheduler(owner)
        next_task = s.mark_task_complete(task)
        assert next_task is not None
        assert next_task.frequency == "Weekly"


class TestConflictDetection:
    def test_detects_close_tasks(self):
        owner = Owner("Lee")
        pet = Pet("Max", "dog")
        pet.add_task(Task("Walk",  time="07:00"))
        pet.add_task(Task("Feed",  time="07:05"))  # 5 min gap → conflict
        owner.add_pet(pet)

        conflicts = Scheduler(owner).detect_conflicts(window_minutes=10)
        assert len(conflicts) == 1

    def test_no_conflict_for_distant_tasks(self, scheduler: Scheduler):
        # Fixture tasks are at 07:00, 12:00, 18:00 — well apart
        conflicts = scheduler.detect_conflicts(window_minutes=10)
        assert conflicts == []

    def test_custom_window(self):
        owner = Owner("Pat")
        pet = Pet("Zoe", "cat")
        pet.add_task(Task("A", time="08:00"))
        pet.add_task(Task("B", time="08:20"))  # 20 min gap
        owner.add_pet(pet)

        s = Scheduler(owner)
        assert s.detect_conflicts(window_minutes=10) == []
        assert len(s.detect_conflicts(window_minutes=25)) == 1
