"""
PawPal+ — Streamlit UI
Connects to the pawpal_system backend to manage pets, tasks, and schedules.
"""

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

# ── Page config ───────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Pet care scheduling made simple.")

# ── Session state: persist Owner across reruns ─
if "owner" not in st.session_state:
    st.session_state.owner = Owner("User")

owner: Owner = st.session_state.owner

# ──────────────────────────────────────────────
# SECTION 1 — Owner name
# ──────────────────────────────────────────────
with st.expander("Owner Settings", expanded=False):
    new_name = st.text_input("Your name", value=owner.name)
    if new_name != owner.name:
        owner.name = new_name

# ──────────────────────────────────────────────
# SECTION 2 — Add a pet
# ──────────────────────────────────────────────
st.subheader("Pets")

with st.form("add_pet_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        pet_name = st.text_input("Pet name", placeholder="e.g. Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"])
    with col3:
        st.write("")  # vertical alignment spacer
        add_pet_btn = st.form_submit_button("Add Pet")

    if add_pet_btn:
        if not pet_name.strip():
            st.warning("Please enter a pet name.")
        elif any(p.name.lower() == pet_name.strip().lower() for p in owner.pets):
            st.warning(f"A pet named '{pet_name.strip()}' already exists.")
        else:
            owner.add_pet(Pet(name=pet_name.strip(), species=species))
            st.success(f"Added {pet_name.strip()} the {species}!")

if owner.pets:
    pet_labels = [f"{p.name} ({p.species})" for p in owner.pets]
    st.write("Your pets: " + ", ".join(pet_labels))
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ──────────────────────────────────────────────
# SECTION 3 — Add a task
# ──────────────────────────────────────────────
st.subheader("Add a Task")

if not owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        pet_options = [p.name for p in owner.pets]
        selected_pet_name = st.selectbox("Assign to pet", pet_options)

        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            description = st.text_input("Task description", placeholder="e.g. Morning walk")
        with col2:
            task_time = st.text_input("Time (HH:MM)", placeholder="07:30")
        with col3:
            frequency = st.selectbox("Frequency", ["None", "Daily", "Weekly"])

        add_task_btn = st.form_submit_button("Add Task")

        if add_task_btn:
            if not description.strip():
                st.warning("Please enter a task description.")
            else:
                # Validate time format
                try:
                    from datetime import datetime
                    datetime.strptime(task_time.strip(), "%H:%M")
                    valid_time = True
                except ValueError:
                    valid_time = False
                    st.warning("Time must be in HH:MM format (e.g. 07:30).")

                if valid_time:
                    freq = None if frequency == "None" else frequency
                    task = Task(
                        description=description.strip(),
                        time=task_time.strip(),
                        frequency=freq,
                    )
                    target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
                    target_pet.add_task(task)
                    st.success(f"Task '{description.strip()}' added to {selected_pet_name}.")

st.divider()

# ──────────────────────────────────────────────
# SECTION 4 — Schedule view
# ──────────────────────────────────────────────
st.subheader("Today's Schedule")

all_pairs = owner.get_all_tasks()

if not all_pairs:
    st.info("No tasks yet. Add pets and tasks above.")
else:
    scheduler = Scheduler(owner)

    # ── Conflict warning ─────────────────────
    conflicts = scheduler.detect_conflicts(window_minutes=10)
    if conflicts:
        for task_a, task_b in conflicts:
            st.warning(
                f"Scheduling conflict: '{task_a.description}' at {task_a.time} "
                f"and '{task_b.description}' at {task_b.time} are within 10 minutes."
            )

    # ── Filter controls ──────────────────────
    col1, col2 = st.columns(2)
    with col1:
        keyword_filter = st.text_input("Filter by keyword", placeholder="e.g. walk")
    with col2:
        status_filter = st.selectbox("Show", ["All", "Pending only", "Completed only"])

    completed_filter = None
    if status_filter == "Pending only":
        completed_filter = False
    elif status_filter == "Completed only":
        completed_filter = True

    filtered = scheduler.filter_tasks(
        keyword=keyword_filter,
        completed=completed_filter,
    )
    sorted_tasks = sorted(
        filtered,
        key=lambda pair: pair[1].time
    )

    if not sorted_tasks:
        st.info("No tasks match the current filter.")
    else:
        # Build a display table grouped by pet
        rows = []
        for pet, task in sorted_tasks:
            rows.append({
                "Pet": pet.name,
                "Time": task.time,
                "Task": task.description,
                "Frequency": task.frequency if task.frequency else "One-time",
                "Done": "Yes" if task.completed else "No",
            })
        st.table(rows)

    # ── Mark task complete ───────────────────
    st.subheader("Mark a Task Complete")

    incomplete = [(pet, task) for pet, task in scheduler.get_all_tasks() if not task.completed]

    if not incomplete:
        st.success("All tasks are complete!")
    else:
        task_labels = [
            f"{pet.name} — {task.time} — {task.description}"
            for pet, task in incomplete
        ]
        chosen_label = st.selectbox("Select task to complete", task_labels)
        chosen_index = task_labels.index(chosen_label)
        chosen_pet, chosen_task = incomplete[chosen_index]

        if st.button("Mark Complete"):
            next_task = scheduler.mark_task_complete(chosen_task)
            st.success(f"Marked '{chosen_task.description}' as done!")
            if next_task:
                st.info(
                    f"Recurring task rescheduled: '{next_task.description}' "
                    f"at {next_task.time} [{next_task.frequency}]"
                )
            st.rerun()
