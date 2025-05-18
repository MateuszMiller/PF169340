import unittest
import tempfile
import os
from koncowy.src.staff import Staff


class TestStaff(unittest.TestCase):

    def setUp(self):
        self.staff = Staff("Anna", "Nowak", "manager")

    def test_staff_default_tasks_and_shifts(self):
        s = Staff("Anna", "Nowak", "worker")
        self.assertEqual(s.tasks_completed, [])
        self.assertEqual(s.shifts, [])

    def test_assign_shift(self):
        test_cases = [
            (
                "assign_valid_shift",
                [("2025-05-20", "10:00")],
                None,
                [("2025-05-20", "10:00")],
            ),
            (
                "get_schedule_after_assign",
                [("2025-05-21", "12:00")],
                "check_schedule",
                [("2025-05-21", "12:00")],
            ),
            (
                "duplicate_shift_should_fail",
                [("2025-05-20", "10:00"), ("2025-05-20", "10:00")],
                ValueError,
                None,
            ),
        ]

        for (case_name, shifts, expected_behavior,
             expected_result) in test_cases:
            with self.subTest(case=case_name):
                staff = Staff("Anna", "Nowak", "manager")  # <<< FIX

                if expected_behavior == ValueError:
                    staff.assign_shift(*shifts[0])
                    with self.assertRaises(ValueError):
                        staff.assign_shift(*shifts[1])
                else:
                    for date, hour in shifts:
                        staff.assign_shift(date, hour)

                    if expected_behavior == "check_schedule":
                        self.assertEqual(staff.get_schedule(), expected_result)
                    else:
                        for shift in expected_result:
                            self.assertIn(shift, staff.shifts)

    def test_clear_schedule(self):
        staff = Staff("Anna", "Nowak", "manager")
        staff.assign_shift("2025-05-20", "10:00")
        staff.assign_shift("2025-05-21", "12:00")
        self.assertTrue(staff.shifts)
        staff.clear_schedule()
        self.assertEqual(len(staff.shifts), 0)

    def test_complete_task(self):
        test_cases = [
            ("valid_task_adds_to_completed",
             "Clean cinema hall", ["Clean cinema hall"], None),
            ("get_completed_tasks_returns_list",
             "Inventory", ["Inventory"], "check_getter"),
            ("empty_task_raises_error", "", None, ValueError),
        ]

        for (case_name, task_name, expected_result,
             expected_behavior) in test_cases:
            with self.subTest(case=case_name):
                staff = Staff("Anna", "Nowak", "manager")

                if expected_behavior == ValueError:
                    with self.assertRaises(ValueError):
                        staff.complete_task(task_name)
                else:
                    staff.complete_task(task_name)
                    if expected_behavior == "check_getter":
                        self.assertEqual(staff.get_completed_tasks(),
                                         expected_result)
                    else:
                        self.assertIn(task_name, staff.tasks_completed)

    def test_is_available(self):
        test_cases = [
            ("not_available_same_day_and_hour",
             [("2025-05-20", "10:00")], "2025-05-20", "10:00", False),
            ("available_different_day", [], "2025-05-21", "10:00", True),
        ]

        for (case_name, preassigned_shifts, check_date,
             check_hour, expected) in test_cases:
            with self.subTest(case=case_name):
                for date, hour in preassigned_shifts:
                    self.staff.assign_shift(date, hour)
                self.assertEqual(self.staff.is_available(check_date,
                                                         check_hour), expected)

    def test_to_dict_contains_expected_fields(self):
        test_cases = [
            ("first_name", "first_name", "Anna"),
            ("last_name", "last_name", "Nowak"),
            ("position", "position", "manager"),
        ]

        for case_name, key, expected_value in test_cases:
            with self.subTest(case=case_name):
                d = self.staff.to_dict()
                self.assertEqual(d[key], expected_value)

    def test_staff_to_dict_returns_dict(self):
        result = self.staff.to_dict()
        self.assertIsInstance(result, dict)

    def test_staff_to_dict_field_types(self):
        data = self.staff.to_dict()
        self.assertIsInstance(data["first_name"], str)
        self.assertIsInstance(data["last_name"], str)
        self.assertIsInstance(data["position"], str)

    def test_save_and_load_json_name(self):
        self.staff.assign_shift("2025-05-20", "10:00")
        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix=".json") as tmp_file:
            tmp_file.close()
            self.staff.save_to_json(tmp_file.name)
            loaded = Staff.read_from_json(tmp_file.name)
            self.assertEqual(loaded.first_name, "Anna")
        os.remove(tmp_file.name)

    def test_save_and_load_json_shifts(self):
        self.staff.assign_shift("2025-05-20", "10:00")
        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix=".json") as tmp_file:
            tmp_file.close()
            self.staff.save_to_json(tmp_file.name)
            loaded = Staff.read_from_json(tmp_file.name)
            self.assertIn(["2025-05-20", "10:00"], loaded.shifts)
        os.remove(tmp_file.name)

    def test_str_contains_first_name(self):
        result = str(self.staff)
        self.assertIn("Anna", result)

    def test_str_ends_with_role(self):
        result = str(self.staff)
        self.assertTrue(result.endswith("manager"))

    def test_should_fail_empty_fields_parametrized(self):
        test_cases = [
            ("empty_first_name", "", "Nowak", "manager"),
            ("empty_last_name", "Anna", "", "manager"),
            ("empty_position", "Anna", "Nowak", ""),
        ]

        for case_name, first_name, last_name, position in test_cases:
            with self.subTest(case=case_name):
                with self.assertRaises(ValueError):
                    Staff(first_name, last_name, position)

    def test_change_position_parametrized(self):
        staff = Staff("Ewa", "Nowak", "worker")

        test_cases = [
            ("change_to_manager", "manager", "manager"),
            ("change_to_empty_should_fail", "", ValueError),
            ("change_to_same_should_fail", "worker", ValueError),
        ]

        for case, new_pos, expected in test_cases:
            with self.subTest(case=case):
                staff.position = "worker"  # reset
                if expected == ValueError:
                    with self.assertRaises(ValueError):
                        staff.change_position(new_pos)
                else:
                    staff.change_position(new_pos)
                    self.assertEqual(staff.position, expected)

    def test_is_manager_parametrized(self):
        test_cases = [
            ("is_manager_true", "manager", True),
            ("is_manager_false_worker", "worker", False),
            ("is_manager_false_random", "cleaner", False),
        ]

        for case, role, expected in test_cases:
            with self.subTest(case=case):
                staff = Staff("A", "B", role)
                self.assertEqual(staff.is_manager(), expected)

    def test_total_hours_assigned(self):
        test_cases = [
            ("no_shifts_assigned", [], 0),
            ("two_shifts_assigned", [("2025-06-01", "08:00"),
                                     ("2025-06-02", "10:00")], 10),
        ]

        for case_name, shifts, expected_total in test_cases:
            with self.subTest(case=case_name):
                for date, hours in shifts:
                    self.staff.assign_shift(date, hours)
                self.assertEqual(self.staff.total_hours_assigned(),
                                 expected_total)

    def test_worked_days_parametrized(self):
        staff = Staff("Zofia", "Lis", "manager")
        staff.assign_shift("2025-05-20", "10:00")
        staff.assign_shift("2025-05-21", "12:00")
        staff.assign_shift("2025-05-20", "14:00")
        self.assertEqual(staff.worked_days(), 2)

    def test_has_task(self):
        test_cases = [
            ("task_completed_should_return_true",
             "Prepare popcorn", True, True),
            ("task_not_assigned_should_return_false",
             "Sweep floors", False, False),
        ]

        for (case_name, task_name, should_complete,
             expected_result) in test_cases:
            with self.subTest(case=case_name):
                if should_complete:
                    self.staff.complete_task(task_name)
                self.assertEqual(self.staff.has_task(task_name),
                                 expected_result)

    def test_staff_str_contains_data(self):
        result = str(self.staff)
        self.assertIsInstance(result, str)
        self.assertIn("Anna", result)
        self.assertIn("Nowak", result)
        self.assertIn("manager", result)


if __name__ == '__main__':
    unittest.main()
