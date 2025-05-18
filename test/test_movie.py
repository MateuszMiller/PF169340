import unittest
import tempfile
import os
import json
from koncowy.src.movie import Movie


class TestMovie(unittest.TestCase):

    def setUp(self):
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

    def test_movie_default_views(self):
        m = Movie("Movie",
                  "Action",
                  120,
                  12,
                  "Director",
                  "EN",
                  2000,
                  7.0,
                  "Desc")
        self.assertEqual(m.views, 0)

    def test_movie_watch_increments_views(self):
        test_cases = [
            ("watch_once", 1, 1),
            ("watch_multiple_times", 5, 5),
            ("watch_zero_times", 0, 0),
        ]

        for case_name, watch_count, expected_views in test_cases:
            with self.subTest(case=case_name):
                movie = Movie("Movie A",
                              "Sci-Fi",
                              148,
                              13,
                              "Director A",
                              "EN",
                              2010,
                              8.8,
                              "Desc")
                for _ in range(watch_count):
                    movie.watch()
                self.assertEqual(movie.views, expected_views)

    def test_is_suitable_for_age(self):
        test_cases = [
            (20, True),
            (10, False),
            (-5, ValueError),
            (13, True),
        ]

        for age, expected in test_cases:
            with ((self.subTest(age=age))):
                if isinstance(expected, bool):
                    self.assertEqual(self.movie.is_suitable_for_age(age),
                                     expected)
                else:
                    with self.assertRaises(expected):
                        self.movie.is_suitable_for_age(age)

    def test_movie_str_representation_contains_fields(self):
        test_cases = [
            ("contains_title", "Inception"),
            ("contains_genre", "Sci-Fi"),
            ("contains_duration", "148 min"),
            ("contains_age_restriction", "13+ age"),
            ("contains_director", "Directed by: Christopher Nolan"),
            ("contains_rating", "Rating: 8.8/10"),
        ]

        movie_str = str(self.movie)

        for case_name, expected_fragment in test_cases:
            with self.subTest(case=case_name):
                self.assertIn(expected_fragment, movie_str)

    def test_movie_with_empty_title_should_fail(self):
        with self.assertRaises(ValueError):
            Movie("",
                  "Action",
                  90,
                  12,
                  "Director",
                  "EN",
                  2000,
                  7.0,
                  "Desc")

    def test_movie_to_dict_fields_parametrized(self):
        test_cases = [
            ("title_field", "title", "Inception"),
            ("duration_field", "duration", 148),
        ]

        for case_name, key, expected_value in test_cases:
            with self.subTest(case=case_name):
                self.assertEqual(self.movie.to_dict()[key], expected_value)

    def test_movie_to_dict_returns_dict(self):
        result = self.movie.to_dict()
        self.assertIsInstance(result, dict)

    def test_movie_to_dict_field_types(self):
        data = self.movie.to_dict()
        self.assertIsInstance(data["title"], str)
        self.assertIsInstance(data["duration"], int)
        self.assertIsInstance(data["rating"], float)
        self.assertIsInstance(data["release_year"], int)

    def test_movie_to_dict_contains_title_key(self):
        d = self.movie.to_dict()
        self.assertIn("title", d)

    def test_save_to_json_and_read(self):

        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix=".json") as tmp_file:
            tmp_file.close()
            self.movie.save_to_json(tmp_file.name)

            loaded_movie = Movie.read_from_json(tmp_file.name)

            self.assertEqual(loaded_movie.title, self.movie.title)
            self.assertEqual(loaded_movie.director, self.movie.director)
            self.assertEqual(loaded_movie.views, self.movie.views)

        os.remove(tmp_file.name)

    def test_save_to_file_and_read(self):
        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix='.txt') as tmp_file:
            tmp_file.close()
            self.movie.save_to_file(tmp_file.name)
            with open(tmp_file.name, 'r') as f:
                content = f.read()
                self.assertIn("Inception", content)
                self.assertIn("Dreams within dreams", content)
        os.remove(tmp_file.name)

    def test_should_fail_missing_views_default_to_zero(self):
        data = {
            "title": "Movie B",
            "genre": "Action",
            "duration": 150,
            "age_restriction": 13,
            "director": "Director B",
            "language": "EN",
            "release_year": 2020,
            "rating": 7.5,
            "description": "Desc"
        }
        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix='.json', mode='w') as tmp_file:
            json.dump(data, tmp_file)
            tmp_file.close()
            movie = Movie.read_from_json(tmp_file.name)
            self.assertEqual(movie.views, 0)
            os.remove(tmp_file.name)

    def test_movie_rating_validation_parametrized(self):
        test_cases = [
            ("rating_too_low", -1, ValueError),
            ("rating_too_high", 10.1, ValueError),
            ("rating_at_lower_bound", 0, 0),
            ("rating_at_upper_bound", 10, 10),
        ]

        for case_name, rating_value, expected in test_cases:
            with self.subTest(case=case_name):
                if (isinstance(expected, type)
                        and issubclass(expected, Exception)):
                    with self.assertRaises(expected):
                        Movie("Movie C",
                              "Action",
                              90,
                              12,
                              "Director C",
                              "EN",
                              2000,
                              rating_value,
                              "Desc")
                else:
                    m = Movie("Movie D",
                              "Action",
                              90,
                              12,
                              "Director D",
                              "EN",
                              2000,
                              rating_value,
                              "Desc")
                    self.assertEqual(m.rating, expected)

    def test_is_in_language_parametrized(self):
        movie = Movie("Movie",
                      "Action",
                      100,
                      12,
                      "Director",
                      "EnGlIsH",
                      2000,
                      7.0,
                      "Desc")
        test_cases = [
            ("exact_match", "EnGlIsH", True),
            ("lowercase_input", "english", True),
            ("wrong_language", "French", False),
            ("empty_input_should_fail", "", ValueError),
        ]

        for case, lang, expected in test_cases:
            with self.subTest(case=case):
                if expected is ValueError:
                    with self.assertRaises(ValueError):
                        movie.is_in_language(lang)
                else:
                    self.assertEqual(movie.is_in_language(lang), expected)

    def test_summary_line(self):
        movie = Movie("Dune",
                      "Sci-Fi",
                      155,
                      14,
                      "Villeneuve",
                      "EN",
                      2021,
                      8.1,
                      "Epic")
        summary = movie.summary_line()
        self.assertEqual(summary, "Dune (2021) - 8.1/10")

    def test_set_description_parametrized(self):
        movie = Movie("Movie",
                      "Action",
                      120,
                      13,
                      "Direcotr",
                      "EN",
                      2010,
                      7.5,
                      "Old description")
        test_cases = [
            ("valid_description", "New description", "New description"),
            ("empty_description_should_fail", "", ValueError),
        ]

        for case, desc, expected in test_cases:
            with self.subTest(case=case):
                if expected is ValueError:
                    with self.assertRaises(ValueError):
                        movie.set_description(desc)
                else:
                    movie.set_description(desc)
                    self.assertEqual(movie.description, expected)

    def test_is_highly_rated_parametrized(self):
        test_cases = [
            ("just_high_enough", 8.0, True),
            ("well_above", 9.3, True),
            ("just_below", 7.9, False),
            ("low", 4.5, False),
        ]

        for case, rating, expected in test_cases:
            with self.subTest(case=case):
                movie = Movie("Movie",
                              "Action",
                              100,
                              12,
                              "Director",
                              "EN",
                              2000,
                              rating,
                              "Desc")
                self.assertEqual(movie.is_highly_rated(), expected)

    def test_long_description(self):
        long_desc = "A" * 1000
        movie = Movie("Movie",
                      "Drama",
                      100,
                      12,
                      "Director",
                      "EN",
                      2005,
                      5.0, long_desc)
        self.assertEqual(movie.description, long_desc)

    def test_non_ascii_characters(self):
        movie = Movie("Amélie",
                      "Comédie",
                      120,
                      12,
                      "Jean-Pierre Jeunet",
                      "Français",
                      2001,
                      8.3,
                      "Une histoire charmante.")
        self.assertIn("Amélie", str(movie))
        self.assertIn("Français", str(movie))

    def test_should_fail_invalid_duration(self):
        with self.assertRaises(ValueError):
            Movie("T",
                  "G", -1,
                  13,
                  "D",
                  "L",
                  2000,
                  5.0,
                  "Desc")

    def test_should_fail_negative_age_restriction(self):
        with self.assertRaises(ValueError):
            Movie("Movie",
                  "Action",
                  90,
                  -1,
                  "Director",
                  "EN",
                  2000,
                  5.0,
                  "Desc")

    def test_should_fail_rating_out_of_range(self):
        with self.assertRaises(ValueError):
            Movie("Movie",
                  "Action",
                  90,
                  12,
                  "Director",
                  "EN",
                  2000,
                  11.0,
                  "Desc")

    def test_is_classic(self):
        test_cases = [
            ("classic_movie",
             Movie("Casablanca",
                   "Drama",
                   100,
                   12,
                   "Curtiz",
                   "EN",
                   1942,
                   8.0,
                   "Old classic"), True),
            ("modern_movie", Movie("Tenet",
                                   "Sci-Fi",
                                   150,
                                   13,
                                   "Nolan",
                                   "EN",
                                   2020,
                                   7.4,
                                   "Modern action"), False),
        ]

        for case_name, movie, expected_result in test_cases:
            with self.subTest(case=case_name):
                self.assertEqual(movie.is_classic(), expected_result)

    def test_increase_rating(self):
        test_data = [
            (0.5, 8.0, 8.5),
            (2.0, 9.5, 10.0),
            (-1.0, 7.0, ValueError)
        ]

        for value, initial, expected in test_data:
            with self.subTest(value=value):
                movie = Movie("Movie",
                              "Action",
                              90,
                              12,
                              "Director",
                              "EN",
                              2000,
                              initial,
                              "Desc")
                if isinstance(expected, float):
                    movie.increase_rating(value)
                    self.assertEqual(movie.rating, expected)
                else:
                    with self.assertRaises(expected):
                        movie.increase_rating(value)

    def test_movie_str_contains_data(self):
        result = str(self.movie)
        self.assertIsInstance(result, str)
        self.assertIn("Inception", result)
        self.assertIn("2010", result)
        self.assertIn("8.8", result)


if __name__ == '__main__':
    unittest.main()
