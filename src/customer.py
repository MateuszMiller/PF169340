import json
import re
from koncowy.src.movie import Movie


class Customer:
    def __init__(self, first_name, last_name, age, email, password):
        if age < 0:
            raise ValueError("Age cannot be negative.")
        if not Customer._validate_email(email):
            raise ValueError("Invalid email format.")

        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.email = email
        self.password = password
        self.is_active = False
        self.ticket_history = []
        self.loyalty_points = 0

    @staticmethod
    def _validate_email(email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def activate_account(self):
        self.is_active = True

    def deactivate_account(self):
        self.is_active = False

    def login(self, email, password):
        if self.email == email and self.password == password:
            if not self.is_active:
                raise ValueError("Account is not active.")
            return True
        raise ValueError("Invalid login credentials.")

    def buy_ticket(self, movie):
        if not isinstance(movie, Movie):
            raise ValueError("Invalid movie object.")
        if self.age < movie.age_restriction:
            raise ValueError("Customer does not meet the "
                             "age restriction for this movie.")
        self.ticket_history.append(movie)
        movie.watch()
        self.loyalty_points += 10
        return True

    def get_watch_history(self):
        return [movie.short_description() for movie in self.ticket_history]

    def get_loyalty_status(self):
        if self.loyalty_points >= 100:
            return "Gold"
        elif self.loyalty_points >= 50:
            return "Silver"
        else:
            return "Bronze"

    def reset_loyalty_points(self):
        self.loyalty_points = 0

    def recommend_movie(self, cinema):
        if not self.ticket_history:
            return None
        fav_genre = max(set(m.genre for m in self.ticket_history),
                        key=lambda g: sum(1 for m in
                                          self.ticket_history if m.genre == g))
        recommended = cinema.get_movies_by_genre(fav_genre)
        return recommended[0] if recommended else None

    def has_ticket_for(self, movie_title):
        return any(m.title == movie_title for m in self.ticket_history)

    def redeem_points(self, points):
        if points <= 0:
            raise ValueError("Points must be positive.")
        if points > self.loyalty_points:
            raise ValueError("Not enough points.")
        self.loyalty_points -= points

    def is_eligible_for_discount(self, min_points):
        if min_points < 0:
            raise ValueError("Minimum points cannot be negative.")
        return self.loyalty_points >= min_points

    def can_watch(self, movie):
        if not isinstance(movie, Movie):
            raise ValueError("Invalid movie object.")
        return self.age >= movie.age_restriction and self.is_active

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "email": self.email,
            "password": self.password,
            "is_active": self.is_active,
            "loyalty_points": self.loyalty_points,
            "watch_history": [movie.to_dict() for movie in self.ticket_history]
        }

    def save_to_json(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)  # type: ignore

    @staticmethod
    def read_from_json(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            customer = Customer(
                data['first_name'],
                data['last_name'],
                data['age'],
                data['email'],
                data['password']
            )
            customer.is_active = data.get('is_active', False)
            customer.loyalty_points = data.get('loyalty_points', 0)
            customer.ticket_history = [
                Movie(
                    m['title'],
                    m['genre'],
                    m['duration'],
                    m['age_restriction'],
                    m['director'],
                    m['language'],
                    m['release_year'],
                    m['rating'],
                    m['description']
                )
                for m in data.get('watch_history', [])
            ]
            return customer

    def __str__(self):
        return (f"Customer: {self.first_name} {self.last_name}, "
                f"{self.age} years old, "
                f"Email: {self.email}, "
                f"Active: {self.is_active}")
