import unittest
import tempfile
import os
from koncowy.src.cinema import Cinema
from koncowy.src.movie import Movie
from koncowy.src.staff import Staff


class TestCinema(unittest.TestCase):

    def setUp(self):
        self.cinema = Cinema("KinoTest", "Testowa 123")
        self.manager = Staff("Anna", "Nowak", "manager")
        self.worker = Staff("Jan", "Kowalski", "worker")
        self.movie = Movie(
            title="Inception",
            genre="Sci-Fi",
            duration=148,
            age_restriction=13,
            director="Christopher Nolan",
            language="English",
            release_year=2010,
            rating=8.8,
            description="Dreams within dreams"
        )

    def test_cinema_default_schedule_and_staff(self):
        c = Cinema("Cinema X", "Street 1")
        self.assertEqual(c.schedule, [])
        self.assertEqual(c.staff, [])

    def test_clear_schedule(self):
        self.cinema.add_movie(self.manager, self.movie)
        self.cinema.clear_schedule()
        self.assertEqual(len(self.cinema.schedule), 0)

    def test_list_current_movies(self):
        test_cases = [
            ("empty_list", [], []),
            ("one_movie", [self.movie], ["Inception"]),
            ("two_movies", [self.movie, Movie("Matrix",
                                              "Sci-Fi",
                                              136,
                                              14,
                                              "Wachowski",
                                              "EN",
                                              1999,
                                              8.7,
                                              "Desc")],
             ["Inception", "Matrix"]),
        ]
        for case, movies, expected_titles in test_cases:
            with self.subTest(case=case):
                cinema = Cinema("Test", "Addr")
                for m in movies:
                    cinema.add_movie(Staff("A", "N", "manager"), m)
                listing = cinema.list_current_movies()
                for title in expected_titles:
                    self.assertTrue(any(title in desc for desc in listing))

    def test_has_movie(self):
        test_cases = [
            ("movie_present_after_add", True, "Inception", True),
            ("movie_absent_without_add", False, "Avatar", False),
            ("movie_absent_completely", False, "Nonexistent", False),
        ]

        for (case_name, should_add_movie,
             title_to_check, expected) in test_cases:
            with self.subTest(case=case_name):
                cinema = Cinema("KinoTest", "Testowa 123")
                manager = Staff("Anna", "Nowak", "manager")
                movie = Movie(
                    title="Inception",
                    genre="Sci-Fi",
                    duration=148,
                    age_restriction=13,
                    director="Christopher Nolan",
                    language="English",
                    release_year=2010,
                    rating=8.8,
                    description="Dreams within dreams"
                )

                if should_add_movie:
                    cinema.add_movie(manager, movie)

                self.assertEqual(cinema.has_movie(title_to_check), expected)

    def test_get_movies_by_genre(self):
        test_cases = [
            ("valid_genre_match", "sci-fi", True, None),
            ("empty_genre_should_fail", "", False, ValueError),
        ]

        for (case_name, genre_input, should_add_movie,
             expected_behavior) in test_cases:
            with self.subTest(case=case_name):
                cinema = Cinema("KinoTest", "Testowa 123")
                manager = Staff("Anna", "Nowak", "manager")
                movie = Movie(
                    title="Inception",
                    genre="Sci-Fi",
                    duration=148,
                    age_restriction=13,
                    director="Christopher Nolan",
                    language="English",
                    release_year=2010,
                    rating=8.8,
                    description="Dreams within dreams"
                )

                if should_add_movie:
                    cinema.add_movie(manager, movie)

                if expected_behavior is ValueError:
                    with self.assertRaises(ValueError):
                        cinema.get_movies_by_genre(genre_input)
                else:
                    result = cinema.get_movies_by_genre(genre_input)
                    self.assertIn(movie, result)

    def test_assign_staff(self):
        test_cases = [
            ("assign_once", 1, 1),
            ("assign_twice_duplicate", 2, 2),
        ]

        for case_name, assign_times, expected_count in test_cases:
            with self.subTest(case=case_name):
                cinema = Cinema("KinoTest", "Testowa 123")
                worker = Staff("Ewa", "Kowalska", "staff")

                for _ in range(assign_times):
                    cinema.assign_staff(worker)

                self.assertEqual(cinema.staff.count(worker), expected_count)

    def test_export_schedule_to_json(self):
        self.cinema.add_movie(self.manager, self.movie)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            path = tmp.name
        self.cinema.export_schedule_to_json(path)
        self.assertTrue(os.path.exists(path))
        with open(path, 'r') as f:
            content = f.read()
        self.assertIn("Inception", content)
        os.remove(path)

    def test_get_movie_details(self):
        self.cinema.add_movie(self.manager, self.movie)
        details = self.cinema.get_movie_details()
        self.assertIn("Inception", details)

    def test_add_movie_with_invalid_arguments(self):
        test_cases = [
            ("none_staff", None, Movie("Inception",
                                       "Sci-Fi",
                                       148,
                                       13,
                                       "Christopher Nolan",
                                       "EN",
                                       2010,
                                       8.8,
                                       "Desc")),
            ("none_movie", Staff("Anna", "Nowak", "manager"), None),
        ]

        for case_name, staff_input, movie_input in test_cases:
            with self.subTest(case=case_name):
                cinema = Cinema("KinoTest", "Testowa 123")
                with self.assertRaises(ValueError):
                    cinema.add_movie(staff_input, movie_input)

    def test_remove_movie_failures(self):
        test_cases = [
            (
                "remove_with_no_permission",
                True,
                "worker",
                PermissionError
            ),
            (
                "remove_nonexistent_movie",
                False,
                "manager",
                ValueError
            ),
        ]

        for (case_name, should_add_movie, remover_role,
             expected_exception) in test_cases:
            with self.subTest(case=case_name):
                cinema = Cinema("KinoTest", "Testowa 123")
                manager = Staff("Anna", "Nowak", "manager")
                worker = Staff("Ewa", "Kowalska", "staff")
                movie = Movie("Inception",
                              "Sci-Fi",
                              148,
                              13,
                              "Christopher Nolan",
                              "EN",
                              2010,
                              8.8,
                              "Desc")

                if should_add_movie:
                    cinema.add_movie(manager, movie)

                remover = manager if remover_role == "manager" else worker

                with self.assertRaises(expected_exception):
                    cinema.remove_movie(remover, movie)

    def test_assign_staff_none_should_fail(self):
        with self.assertRaises(ValueError):
            self.cinema.assign_staff(None)

    def test_add_duplicate_staff_should_fail(self):
        self.cinema.add_staff_member(self.manager, self.worker)
        with self.assertRaises(ValueError):
            self.cinema.add_staff_member(self.manager, self.worker)

    def test_choose_movies_to_play(self):
        test_cases = [
            (
                "valid_movies_chosen",
                "manager",
                lambda m: [m, Movie("Matrix",
                                    "Sci-Fi",
                                    136,
                                    14,
                                    "Wachowski",
                                    "English",
                                    1999,
                                    8.7,
                                    "Reality is an illusion")],
                None  # brak wyjątku
            ),
            (
                "movies_list_is_none",
                "manager",
                lambda m: None,
                ValueError
            ),
            (
                "called_by_non_manager",
                "worker",
                lambda m: [],
                PermissionError
            ),
            (
                "movie_list_contains_none",
                "manager",
                lambda m: [None],
                ValueError
            ),
        ]

        for (case_name, staff_type, movie_list_func,
             expected_exception) in test_cases:
            with self.subTest(case=case_name):
                cinema = Cinema("KinoTest", "Testowa 123")
                manager = Staff("Anna", "Nowak", "manager")
                worker = Staff("Ewa", "Kowalska", "staff")
                inception = Movie("Inception",
                                  "Sci-Fi",
                                  148,
                                  13,
                                  "Christopher Nolan",
                                  "English",
                                  2010,
                                  8.8,
                                  "Mind-bending")

                cinema.add_movie(manager, inception)

                user = manager if staff_type == "manager" else worker
                movie_list = movie_list_func(inception)

                if expected_exception:
                    with self.assertRaises(expected_exception):
                        cinema.choose_movies_to_play(user, movie_list)
                else:
                    cinema.choose_movies_to_play(user, movie_list)
                    for m in movie_list:
                        self.assertIn(m, cinema.schedule)

    def test_to_dict_contents(self):
        self.cinema.add_movie(self.manager, self.movie)
        self.cinema.assign_staff(self.worker)
        d = self.cinema.to_dict()
        self.assertEqual(d["name"], "KinoTest")
        self.assertEqual(len(d["schedule"]), 1)
        self.assertEqual(len(d["staff"]), 1)

    def test_cinema_to_dict_returns_dict(self):
        self.cinema.add_movie(self.manager, self.movie)
        self.cinema.assign_staff(self.worker)
        result = self.cinema.to_dict()
        self.assertIsInstance(result, dict)

    def test_cinema_to_dict_field_types(self):
        self.cinema.add_movie(self.manager, self.movie)
        self.cinema.assign_staff(self.worker)
        data = self.cinema.to_dict()
        self.assertIsInstance(data["name"], str)
        self.assertIsInstance(data["address"], str)
        self.assertIsInstance(data["schedule"], list)
        self.assertIsInstance(data["staff"], list)

    def test_save_and_read_from_json(self):
        self.cinema.add_movie(self.manager, self.movie)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            path = tmp.name
        self.cinema.save_to_json(path)
        loaded = Cinema.read_from_json(path)
        self.assertEqual(loaded.name, self.cinema.name)
        self.assertEqual(len(loaded.schedule), 1)
        os.remove(path)

    def test_save_to_file_and_str(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            path = tmp.name
        self.cinema.save_to_file(path)
        with open(path, 'r') as f:
            content = f.read()
        self.assertIn("KinoTest", content)
        self.assertEqual(str(self.cinema), "Cinema: KinoTest, Testowa 123")
        os.remove(path)

    def test_read_from_json_incomplete_movie_data_should_fail(self):
        import json
        incomplete_data = {
            "name": "KinoTest",
            "address": "Testowa 123",
            "schedule": [
                {
                    "title": "Broken Movie",
                    "genre": "Sci-Fi"
                }
            ]
        }
        path = tempfile.mktemp(suffix=".json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(incomplete_data, f)  # type: ignore
        with self.assertRaises(KeyError):
            Cinema.read_from_json(path)
        os.remove(path)

    def test_export_schedule_to_json_structure(self):
        import json
        self.cinema.add_movie(self.manager, self.movie)
        path = tempfile.mktemp(suffix=".json")
        self.cinema.export_schedule_to_json(path)
        with open(path, 'r') as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertEqual(data[0]["title"], "Inception")
        self.assertEqual(data[0]["director"], "Christopher Nolan")
        os.remove(path)

    def test_add_movie_with_invalid_role_should_fail(self):
        technician = Staff("Ola", "Tester", "technician")
        with self.assertRaises(PermissionError):
            self.cinema.add_movie(technician, self.movie)

    def test_str_output_format(self):
        result = str(self.cinema)
        self.assertTrue(result.startswith("Cinema:"))
        self.assertIn(self.cinema.name, result)
        self.assertIn(self.cinema.address, result)

    def test_count_movies_by_genre(self):
        test_cases = [
            ("sci-fi_and_romance", [("Sci-Fi", 2), ("Romance", 1)]),
            ("only_sci-fi", [("Sci-Fi", 3)]),
        ]
        for case, genre_counts in test_cases:
            with self.subTest(case=case):
                cinema = Cinema("C", "A")
                manager = Staff("M", "G", "manager")
                for genre, count in genre_counts:
                    for i in range(count):
                        cinema.add_movie(manager, Movie(f"T{i}",
                                                        genre,
                                                        100,
                                                        13,
                                                        "D",
                                                        "EN",
                                                        2000,
                                                        8.0,
                                                        "Desc"))
                counts = cinema.count_movies_by_genre()
                for genre, count in genre_counts:
                    self.assertEqual(counts[genre], count)

    def test_remove_staff_member_by_name(self):
        test_cases = [
            ("existing_staff", "Anna", "Nowak", True, True),
            ("nonexistent_staff", "Ghost", "Person", False, False),
        ]
        for case, first, last, should_add, expect_removed in test_cases:
            with self.subTest(case=case):
                cinema = Cinema("KinoTest", "Testowa 123")
                staff = Staff(first, last, "manager")

                if should_add:
                    cinema.assign_staff(staff)

                initial_count = sum(1 for s in cinema.staff
                                    if s.first_name == first
                                    and s.last_name == last)

                cinema.remove_staff_member_by_name(first, last)

                final_count = sum(1 for s in cinema.staff
                                  if s.first_name == first
                                  and s.last_name == last)

                if expect_removed:
                    self.assertEqual(final_count, initial_count - 1)
                else:
                    self.assertEqual(final_count, initial_count)

    def test_get_movies_by_genre_on_empty_schedule(self):
        result = self.cinema.get_movies_by_genre("Drama")
        self.assertEqual(result, [])

    def test_add_staff_member_success(self):
        self.cinema.add_staff_member(self.manager, self.worker)
        self.assertIn(self.worker, self.cinema.staff)

    def test_remove_movie(self):
        test_cases = [
            ("remove_existing", True, False),
            ("remove_nonexistent", False, True),
        ]
        for case, add_first, should_raise in test_cases:
            with self.subTest(case=case):
                cinema = Cinema("X", "Y")
                manager = Staff("A", "B", "manager")
                movie = Movie("T", "G", 90, 13, "D", "L", 2000, 8.0, "Desc")
                if add_first:
                    cinema.add_movie(manager, movie)
                    cinema.remove_movie(manager, movie)
                if should_raise:
                    with self.assertRaises(ValueError):
                        cinema.remove_movie(manager, movie)

    def test_remove_all_movies(self):
        cinema = Cinema("KinoTest", "Testowa 123")
        manager = Staff("Anna", "Nowak", "manager")
        worker = Staff("Jan", "Kowalski", "staff")
        movie1 = Movie("Inception",
                       "Sci-Fi",
                       148,
                       13,
                       "Nolan",
                       "EN",
                       2010,
                       8.8,
                       "Desc")
        movie2 = Movie("Titanic",
                       "Drama",
                       195,
                       13,
                       "Cameron",
                       "EN",
                       1997,
                       9.0,
                       "Desc")
        cinema.schedule = [movie1, movie2]

        test_cases = [
            ("manager_can_clear_schedule", manager, True, 0),
            ("non_manager_cannot_clear_schedule", worker, False, 2),
        ]

        for case, user, should_succeed, expected_count in test_cases:
            with self.subTest(case=case):
                cinema.schedule = [movie1, movie2]
                if should_succeed:
                    cinema.remove_all_movies(user)
                    self.assertEqual(len(cinema.schedule), expected_count)
                else:
                    with self.assertRaises(PermissionError):
                        cinema.remove_all_movies(user)
                    self.assertEqual(len(cinema.schedule), expected_count)

    def test_choose_movies_to_play_exact_list(self):
        movie2 = Movie("Interstellar",
                       "Sci-Fi",
                       170,
                       13,
                       "Nolan",
                       "EN",
                       2014,
                       8.6,
                       "Space")
        movie3 = Movie("The Matrix",
                       "Sci-Fi",
                       136,
                       16,
                       "Wachowski",
                       "EN",
                       1999,
                       8.7,
                       "Virtual reality")
        self.cinema.choose_movies_to_play(self.manager, [movie2, movie3])
        self.assertEqual(self.cinema.schedule, [movie2, movie3])

    def test_get_movies_by_genre_match(self):
        self.cinema.add_movie(self.manager, self.movie)
        results = self.cinema.get_movies_by_genre("Sci-Fi")
        self.assertIn(self.movie, results)

    def test_get_movie_by_title(self):
        cinema = Cinema("KinoTest", "Testowa 123")
        manager = Staff("Anna", "Nowak", "manager")
        movie1 = Movie("Inception",
                       "Sci-Fi",
                       148,
                       13,
                       "Nolan",
                       "EN",
                       2010,
                       8.8,
                       "Desc")
        movie2 = Movie("Interstellar",
                       "Sci-Fi",
                       169,
                       13,
                       "Nolan",
                       "EN",
                       2014,
                       8.6,
                       "Desc")
        cinema.add_movie(manager, movie1)
        cinema.add_movie(manager, movie2)

        test_cases = [
            ("exact_match", "Inception", movie1),
            ("case_insensitive", "interstellar", movie2),
        ]

        for case, title, expected in test_cases:
            with self.subTest(case=case):
                result = cinema.get_movie_by_title(title)
                self.assertEqual(result, expected)

    def test_add_staff_member_distinct(self):
        new_staff = Staff("Zofia", "Lis", "worker")
        self.cinema.add_staff_member(self.manager, new_staff)
        self.assertIn(new_staff, self.cinema.staff)

    def test_get_staff_by_role(self):
        cinema = Cinema("KinoTest", "Testowa 123")
        staff1 = Staff("Anna", "Nowak", "manager")
        staff2 = Staff("Ewa", "Kowalska", "worker")
        staff3 = Staff("John", "Smith", "manager")
        cinema.assign_staff(staff1)
        cinema.assign_staff(staff2)
        cinema.assign_staff(staff3)

        test_cases = [
            ("managers", "manager", [staff1, staff3]),
            ("workers", "worker", [staff2]),
        ]

        for case, role, expected in test_cases:
            with self.subTest(case=case):
                result = cinema.get_staff_by_role(role)
                self.assertEqual(result, expected)

    def test_choose_movies_to_play_empty_list(self):
        self.cinema.choose_movies_to_play(self.manager, [])
        self.assertEqual(self.cinema.schedule, [])

    def test_choose_movies_to_play_valid_list(self):
        movie2 = Movie("Dune",
                       "Sci-Fi",
                       155,
                       14,
                       "Villeneuve",
                       "EN",
                       2021,
                       8.1,
                       "Epic saga")
        self.cinema.choose_movies_to_play(self.manager, [self.movie, movie2])
        self.assertEqual(len(self.cinema.schedule), 2)
        self.assertIn(movie2, self.cinema.schedule)

    def test_cinema_str_contains_data(self):
        result = str(self.cinema)
        self.assertIsInstance(result, str)
        self.assertIn("KinoTest", result)
        self.assertIn("Testowa 123", result)


if __name__ == '__main__':
    unittest.main()
