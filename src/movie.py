import json


class Movie:
    def __init__(self, title, genre, duration, age_restriction,
                 director, language, release_year, rating, description):
        if duration <= 0:
            raise ValueError("Duration must be a positive number.")
        if age_restriction < 0:
            raise ValueError("Age restriction cannot be negative.")
        if not (0 <= rating <= 10):
            raise ValueError("Rating must be between 0 and 10.")
        if not title or not isinstance(title, str):
            raise ValueError("Title cannot be empty.")
        self.title = title
        self.genre = genre
        self.duration = duration
        self.age_restriction = age_restriction
        self.director = director
        self.language = language
        self.release_year = release_year
        self.rating = rating
        self.description = description
        self.views = 0

    def watch(self):
        self.views += 1

    def is_suitable_for_age(self, age):
        if age < 0:
            raise ValueError("Age cannot be negative.")
        return age >= self.age_restriction

    def short_description(self):
        return f"{self.title} ({self.genre}, {self.release_year})"

    def is_classic(self):
        return self.release_year < 2000

    def increase_rating(self, value):
        if value < 0:
            raise ValueError("Cannot increase by negative value.")
        self.rating = min(10, self.rating + value)

    def is_highly_rated(self):
        return self.rating >= 8.0

    def is_in_language(self, language):
        if not language:
            raise ValueError("Language cannot be empty.")
        return self.language.lower() == language.lower()

    def summary_line(self):
        return f"{self.title} ({self.release_year}) - {self.rating}/10"

    def set_description(self, new_description):
        if not new_description:
            raise ValueError("Description cannot be empty.")
        self.description = new_description

    def to_dict(self):
        return self.__dict__

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            f.write(str(self))

    def save_to_json(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)  # type: ignore

    @staticmethod
    def read_from_json(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        views = data.pop("views", 0)
        movie = Movie(**data)
        movie.views = views
        return movie

    def __str__(self):
        return (
            f"{self.title} ({self.genre}, "
            f"{self.duration} min, "
            f"{self.age_restriction}+ age)\n"
            f"Directed by: {self.director}, "
            f"Language: {self.language}, "
            f"Year: {self.release_year}\n"
            f"Rating: {self.rating}/10, "
            f"Views: {self.views}\n"
            f"Description: {self.description}"
        )
