from datetime import datetime, timedelta


class StudyTools:

    def __init__(self, memory):
        self.memory = memory

    # =========================================================
    # TOOL 1: ADD STUDY TASK
    # =========================================================

    def add_task(self, subject, task, deadline, estimated_hours):

        # Validate deadline
        try:
            datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            return {
                "success": False,
                "error": "Deadline must be in YYYY-MM-DD format."
            }

        # Validate study hours
        if estimated_hours <= 0:
            return {
                "success": False,
                "error": "Estimated hours must be greater than 0."
            }

        # Create task
        task_data = {
            "subject": subject,
            "task": task,
            "deadline": deadline,
            "estimated_hours": estimated_hours
        }

        # Store task in memory
        task_id = self.memory.add_task(task_data)

        return {
            "success": True,
            "task_id": task_id,
            "message": f"{subject} task added successfully."
        }


    # =========================================================
    # TOOL 2: BUILD STUDY SCHEDULE
    # =========================================================

    def build_schedule(
        self,
        daily_hours=3,
        start_date=None,
        custom_hours=None
    ):

        # Get all stored tasks
        tasks = list(self.memory.get_tasks().values())

        # Check if tasks exist
        if not tasks:
            return {
                "success": False,
                "error": "No study tasks found."
            }

        # Validate default daily hours
        if daily_hours <= 0:
            return {
                "success": False,
                "error": "Daily study hours must be greater than 0."
            }

        # -----------------------------------------------------
        # Start date
        # -----------------------------------------------------

        if start_date is None:
            start_date = datetime.now().date()

        else:
            try:
                start_date = datetime.strptime(
                    start_date,
                    "%Y-%m-%d"
                ).date()

            except ValueError:
                return {
                    "success": False,
                    "error": "Start date must be in YYYY-MM-DD format."
                }

        # -----------------------------------------------------
        # Custom hours
        # Example:
        #
        # {
        #     "2026-09-04": 6,
        #     "2026-09-05": 5
        # }
        # -----------------------------------------------------

        if custom_hours is None:
            custom_hours = {}

        # Validate custom hours
        for date, hours in custom_hours.items():

            try:
                datetime.strptime(
                    date,
                    "%Y-%m-%d"
                )

            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid custom date: {date}"
                }

            if hours <= 0:
                return {
                    "success": False,
                    "error": f"Study hours for {date} must be greater than 0."
                }

        # -----------------------------------------------------
        # Sort tasks by deadline
        # Earliest deadline = highest priority
        # -----------------------------------------------------

        tasks.sort(
            key=lambda task: task["deadline"]
        )

        # -----------------------------------------------------
        # Track remaining hours for each task
        # -----------------------------------------------------

        remaining_hours = {}

        for task_id, task in enumerate(tasks):
            remaining_hours[task_id] = task["estimated_hours"]

        # -----------------------------------------------------
        # Create schedule
        # -----------------------------------------------------

        schedule = []

        current_date = start_date

        # Maximum planning period = 365 days
        for _ in range(365):

            date_string = current_date.strftime("%Y-%m-%d")

            # Use custom hours if the user provided them.
            # Otherwise use normal daily hours.
            available_hours = custom_hours.get(
                date_string,
                daily_hours
            )

            # -------------------------------------------------
            # Give study time to tasks
            # based on deadline priority
            # -------------------------------------------------

            for task_id, task in enumerate(tasks):

                # Task already completed
                if remaining_hours[task_id] <= 0:
                    continue

                # Convert deadline to date
                deadline = datetime.strptime(
                    task["deadline"],
                    "%Y-%m-%d"
                ).date()

                # Never schedule after deadline
                if current_date > deadline:
                    continue

                # No study time remaining today
                if available_hours <= 0:
                    break

                # Calculate today's study hours
                hours = min(
                    remaining_hours[task_id],
                    available_hours
                )

                # Add to schedule
                schedule.append({
                    "date": date_string,
                    "subject": task["subject"],
                    "task": task["task"],
                    "hours": hours,
                    "deadline": task["deadline"]
                })

                # Update remaining hours
                remaining_hours[task_id] -= hours

                # Reduce today's available time
                available_hours -= hours

            # -------------------------------------------------
            # Stop if all tasks are completed
            # -------------------------------------------------

            if all(
                hours <= 0
                for hours in remaining_hours.values()
            ):
                break

            # Move to next day
            current_date += timedelta(days=1)

        # -----------------------------------------------------
        # Find tasks that could not fit before deadline
        # -----------------------------------------------------

        unscheduled = []

        for task_id, task in enumerate(tasks):

            if remaining_hours[task_id] > 0:

                unscheduled.append({
                    "subject": task["subject"],
                    "task": task["task"],
                    "remaining_hours": remaining_hours[task_id],
                    "deadline": task["deadline"]
                })

        # -----------------------------------------------------
        # Return structured result
        # -----------------------------------------------------

        return {
            "success": True,
            "schedule": schedule,
            "unscheduled": unscheduled
        }