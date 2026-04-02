"""
PawPal+ — Demo Script
Creates an owner, 2 pets, and several tasks, then demonstrates
sorting, filtering, conflict detection, and task completion.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # ── Setup ──────────────────────────────────
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="dog")
    luna  = Pet(name="Luna",  species="cat")

    owner.add_pet(mochi)
    owner.add_pet(luna)

    # ── Tasks for Mochi ────────────────────────
    mochi.add_task(Task("Morning walk",        time="07:00", frequency="Daily"))
    mochi.add_task(Task("Breakfast feeding",   time="07:30", frequency="Daily"))
    mochi.add_task(Task("Heartworm pill",      time="08:00", frequency="Weekly"))
    mochi.add_task(Task("Afternoon walk",      time="15:00", frequency="Daily"))
    mochi.add_task(Task("Vet appointment",     time="10:00"))

    # ── Tasks for Luna ─────────────────────────
    luna.add_task(Task("Breakfast feeding",    time="07:05", frequency="Daily"))
    luna.add_task(Task("Flea medication",      time="09:00", frequency="Weekly"))
    luna.add_task(Task("Evening feeding",      time="18:00", frequency="Daily"))

    scheduler = Scheduler(owner)

    # ── Full sorted schedule ───────────────────
    scheduler.print_schedule()

    # ── Conflict detection ─────────────────────
    conflicts = scheduler.detect_conflicts(window_minutes=10)
    print("Potential scheduling conflicts (within 10 min):")
    if conflicts:
        for a, b in conflicts:
            print(f"  !! {a.time} '{a.description}'  <->  {b.time} '{b.description}'")
    else:
        print("  None found.")
    print()

    # ── Filter: incomplete walk tasks ──────────
    walks = scheduler.filter_tasks(keyword="walk", completed=False)
    print(f"Pending walk tasks ({len(walks)}):")
    for pet, task in walks:
        print(f"  {pet.name}: {task}")
    print()

    # ── Mark a recurring task complete ─────────
    morning_walk = mochi.tasks[0]
    print(f"Completing: '{morning_walk.description}' ...")
    next_task = scheduler.mark_task_complete(morning_walk)
    if next_task:
        print(f"  -> Next occurrence scheduled at {next_task.time} [{next_task.frequency}]")
    print()

    # ── Updated schedule after completion ──────
    print("Updated schedule (completed tasks shown with [X]):")
    scheduler.print_schedule()


if __name__ == "__main__":
    main()
