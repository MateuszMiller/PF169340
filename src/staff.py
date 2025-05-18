import json


class Staff:
    def __init__(self, first_name, last_name, position):
        if not first_name or not last_name or not position:
            raise ValueError("First name, "
                             "last name and position cannot be empty.")
        self.first_name = first_name
        self.last_name = last_name
        self.position = position
        self.shifts = []
        self.tasks_completed = []

    def assign_shift(self, date, time):
        if (date, time) in self.shifts:
            raise ValueError("Shift already assigned for this date and time.")
        self.shifts.append((date, time))

    def is_manager(self):
        return self.position.lower() == "manager"

    def complete_task(self, task):
        if not task:
            raise ValueError("Task cannot be empty.")
        self.tasks_completed.append(task)

    def get_completed_tasks(self):
        return self.tasks_completed

    def is_available(self, date, time):
        return (date, time) not in self.shifts

    def get_schedule(self):
        return self.shifts

    def clear_schedule(self):
        self.shifts = []

    def total_hours_assigned(self):
        return len(self.shifts) * 5  # jedna zmiana = 5h

    def worked_days(self):
        return len(set(date for date, _ in self.shifts))

    def has_task(self, task):
        return task in self.tasks_completed

    def reset_tasks(self):
        self.tasks_completed = []

    def change_position(self, new_position):
        if not new_position:
            raise ValueError("New position cannot be empty.")
        if new_position == self.position:
            raise ValueError("New position must be "
                             "different from current one.")
        self.position = new_position

    def to_dict(self):
        return self.__dict__

    def save_to_json(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)  # type: ignore

    @staticmethod
    def read_from_json(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            staff = Staff(data['first_name'],
                          data['last_name'], data['position'])
            staff.shifts = data.get('shifts', [])
            staff.tasks_completed = data.get('tasks_completed', [])
            return staff

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position}"
