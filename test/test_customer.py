import unittest
import tempfile
import os
from koncowy.src.customer import Customer
from koncowy.src.movie import Movie


class TestCustomer(unittest.TestCase):

    def setUp(self):
        self.customer = Customer("John",
                                 "Doe",
                                 25,
                                 "john.doe@example.com",
                                 "password123")

    def test_customer_default_state(self):
        c = Customer("John",
                     "Doe",
                     25,
                     "john.doe@example.com",
                     "password123")
        self.assertFalse(c.is_active)
        self.assertEqual(c.loyalty_points, 0)

    def test_invalid_age(self):
        with self.assertRaises(ValueError):
            Customer("Jane",
                     "Doe", -1,
                     "jane@example.com",
                     "pass")

    def test_can_watch_parametrized(self):
        movie = Movie("Film",
                      "Drama",
                      100,
                      18,
                      "Director",
                      "EN",
                      2020,
                      7.5,
                      "Desc")
        test_cases = [
            ("eligible_and_active", 20, True, True),
            ("too_young", 15, True, False),
            ("inactive_account", 25, False, False),
            ("invalid_object", 25, True, ValueError)
        ]

        for case, age, active, expected in test_cases:
            with self.subTest(case=case):
                self.customer.age = age
                self.customer.is_active = active
                if expected is ValueError:
                    with self.assertRaises(ValueError):
                        self.customer.can_watch("not a movie")
                else:
                    self.assertEqual(self.customer.can_watch(movie), expected)

    def test_full_name(self):
        self.assertEqual(self.customer.full_name(), "John Doe")

    def test_email_validation_parametrized(self):
        test_cases = [
            ("missing_at", "invalidemail.com"),
            ("missing_domain", "name@"),
            ("no_local_part", "@domain.com"),
            ("just_text", "email"),
        ]

        for case, email in test_cases:
            with self.subTest(case=case):
                with self.assertRaises(ValueError):
                    Customer("Jan", "Nowak", 25, email, "somepass")

    def test_login_parametrized(self):
        test_cases = [
            ("login_success",
             True,
             "john.doe@example.com",
             "password123",
             True),
            ("wrong_password",
             True,
             "john.doe@example.com",
             "wrongpassword",
             ValueError),
            ("wrong_email",
             True,
             "nonexistent@example.com",
             "password123",
             ValueError),
            ("inactive_account",
             False,
             "john.doe@example.com",
             "password123",
             ValueError),
        ]

        for case, activate, email, password, expected in test_cases:
            with self.subTest(case=case):

                self.customer = Customer("John",
                                         "Doe",
                                         25,
                                         "john.doe@example.com",
                                         "password123")

                if activate:
                    self.customer.activate_account()

                if expected is True:
                    self.assertTrue(self.customer.login(email, password))
                else:
                    with self.assertRaises(expected):
                        self.customer.login(email, password)

    def test_login_case_sensitive_email(self):
        self.customer.activate_account()
        with self.assertRaises(ValueError):
            self.customer.login("John.Doe@Example.com", "password123")

    def test_account_activation(self):
        self.customer.activate_account()
        self.assertTrue(self.customer.is_active)

    def test_account_deactivation(self):
        self.customer.activate_account()
        self.customer.deactivate_account()
        self.assertFalse(self.customer.is_active)

    def test_buy_ticket(self):
        test_cases = [
            ("valid_movie",
             Movie("Movie A",
                   "Action",
                   120,
                   18,
                   "Director A",
                   "EN",
                   2022,
                   8.0,
                   "Description A"), True),
            (
            "age_restricted",
            Movie("Movie B",
                  "Drama",
                  120,
                  30,
                  "Director B",
                  "EN",
                  2020,
                  7.5,
                  "Description B"), ValueError),
            ("invalid_object", "NotAMovie", ValueError),
        ]

        for case_name, movie_input, expected in test_cases:
            with self.subTest(case=case_name):
                if case_name == "valid_movie":
                    self.customer.activate_account()
                if expected is True:
                    result = self.customer.buy_ticket(movie_input)
                    self.assertTrue(result)
                    self.assertEqual(len(self.customer.ticket_history), 1)
                    self.assertEqual(self.customer.loyalty_points, 10)
                else:
                    with self.assertRaises(expected):
                        self.customer.buy_ticket(movie_input)

    def test_loyalty_status(self):
        test_cases = [
            (0, "Bronze"),
            (50, "Silver"),
            (100, "Gold")
        ]

        for points, expected in test_cases:
            with self.subTest(points=points):
                self.customer.loyalty_points = points
                self.assertEqual(self.customer.get_loyalty_status(), expected)

    def test_recommend_movie_various_cases(self):
        movie1 = Movie("Movie C",
                       "Comedy",
                       90,
                       10,
                       "Director C",
                       "EN",
                       2021,
                       7.0,
                       "Description C")
        movie2 = Movie("Movie D",
                       "Comedy",
                       100,
                       10,
                       "Director D",
                       "EN",
                       2021,
                       7.1,
                       "Description D")
        movie3 = Movie("M3",
                       "Horror",
                       100,
                       10,
                       "Director E",
                       "EN",
                       2020,
                       6.5,
                       "Description E")

        test_cases = [
            ("success_recommend", [movie1, movie2], ["Comedy"], movie1),
            ("fail_no_history", [], ["Any"], None),
            ("fail_no_match", [movie3], [], None)
        ]

        for case_name, history, genres_available, expected in test_cases:
            with self.subTest(case=case_name):
                self.customer.ticket_history = history

                class Cinema:
                    @staticmethod
                    def get_movies_by_genre(genre):
                        return [m for m in [movie1, movie2, movie3]
                                if m.genre in genres_available
                                and m.genre == genre]

                cinema = Cinema()
                result = self.customer.recommend_movie(cinema)
                self.assertEqual(result, expected)

    def test_to_dict(self):
        data = self.customer.to_dict()
        self.assertEqual(data['first_name'], "John")
        self.assertEqual(data['loyalty_points'], 0)

    def test_customer_to_dict_returns_dict(self):
        result = self.customer.to_dict()
        self.assertIsInstance(result, dict)

    def test_customer_to_dict_field_types(self):
        data = self.customer.to_dict()
        self.assertIsInstance(data["first_name"], str)
        self.assertIsInstance(data["email"], str)
        self.assertIsInstance(data["loyalty_points"], int)
        self.assertIsInstance(data["is_active"], bool)

    def test_json_serialization_and_reading(self):
        movie = Movie("Movie F",
                      "Action",
                      100,
                      10,
                      "Director F",
                      "EN",
                      2023,
                      9.0,
                      "Description F")
        self.customer.ticket_history = [movie]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            tmp_path = tmp.name

        self.customer.save_to_json(tmp_path)
        loaded = Customer.read_from_json(tmp_path)
        self.assertEqual(loaded.first_name, self.customer.first_name)
        self.assertEqual(len(loaded.ticket_history), 1)
        os.remove(tmp_path)

    def test_ticket_and_has_ticket_logic(self):
        movie = Movie("Movie G",
                      "Sci-Fi",
                      169,
                      13,
                      "Director G",
                      "EN",
                      2014,
                      9.0,
                      "Desc")

        test_cases = [
            ("buy_and_check_length", movie, True),
            ("has_ticket_found", movie, True),
            ("has_ticket_not_found", "Unknown Movie", False)
        ]

        for case, data, expected in test_cases:
            with self.subTest(case=case):
                if case == "buy_and_check_length":
                    self.customer.activate_account()
                    original_len = len(self.customer.ticket_history)
                    self.customer.buy_ticket(data)
                    self.assertEqual(len
                                     (self.customer.ticket_history),
                                     original_len + 1)

                elif case == "has_ticket_found":
                    self.customer.activate_account()
                    self.customer.buy_ticket(data)
                    self.assertTrue(self.customer.has_ticket_for(data.title))

                elif case == "has_ticket_not_found":
                    self.assertFalse(self.customer.has_ticket_for(data))

    def test_redeem_points(self):
        test_cases = [
            (40, 30, 10),
            (10, 20, ValueError),
            (10, -5, ValueError)
        ]

        for initial, redeem, expected in test_cases:
            with self.subTest(initial_points=initial, redeem=redeem):
                self.customer.loyalty_points = initial
                if isinstance(expected, int):
                    self.customer.redeem_points(redeem)
                    self.assertEqual(self.customer.loyalty_points, expected)
                else:
                    with self.assertRaises(expected):
                        self.customer.redeem_points(redeem)

    def test_reset_loyalty_points(self):
        self.customer.loyalty_points = 80
        self.customer.reset_loyalty_points()
        self.assertEqual(self.customer.loyalty_points, 0)

    def test_is_eligible_for_discount_parametrized(self):
        test_cases = [
            ("eligible", 100, 50, True),
            ("not_eligible", 30, 50, False),
            ("equal_threshold", 50, 50, True),
            ("negative_threshold", 50, -1, ValueError),
        ]
        for case, points, threshold, expected in test_cases:
            with self.subTest(case=case):
                self.customer.loyalty_points = points
                if expected is ValueError:
                    with self.assertRaises(ValueError):
                        self.customer.is_eligible_for_discount(threshold)
                else:
                    self.assertEqual(
                        self.customer.is_eligible_for_discount(threshold),
                        expected)

    def test_customer_str_contains_data(self):
        result = str(self.customer)
        self.assertIsInstance(result, str)
        self.assertIn("John", result)
        self.assertIn("Doe", result)
        self.assertIn("john.doe@example.com", result)


if __name__ == '__main__':
    unittest.main()
