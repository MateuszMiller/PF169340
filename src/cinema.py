import json
from koncowy.src.movie import Movie


class Cinema:
    def __init__(self, name, address):
        if not name or not address:
            raise ValueError("Cinema name and address cannot be empty.")
        self.name = name
        self.address = address
        self.schedule = []
        self.staff = []

    def __str__(self):
        return f"Cinema: {self.name}, {self.address}"

    def assign_staff(self, staff_member):
        if staff_member is None:
            raise ValueError("Staff member cannot be None.")
        self.staff.append(staff_member)

    def get_staff_by_role(self, role):
        if not role or not isinstance(role, str):
            raise ValueError("Invalid role.")
        return [s for s in self.staff if s.position.lower() == role.lower()]

    def add_staff_member(self, staff_member_requesting, staff_member_to_add):
        if staff_member_requesting is None or staff_member_to_add is None:
            raise ValueError("Staff members cannot be None.")
        if staff_member_requesting.position.lower() != "manager":
            raise PermissionError("Only managers can add staff members.")
        if staff_member_to_add in self.staff:
            raise ValueError("Staff member is already added.")
        self.staff.append(staff_member_to_add)

    def add_movie(self, staff_member, movie):
        if staff_member is None or movie is None:
            raise ValueError("Staff member and movie cannot be None.")
        if staff_member.position.lower() != "manager":
            raise PermissionError("Only managers can add movies.")
        if movie in self.schedule:
            raise ValueError("Movie is already in the schedule.")
        self.schedule.append(movie)

    def remove_movie(self, staff_member, movie):
        if staff_member is None or movie is None:
            raise ValueError("Staff member and movie cannot be None.")
        if staff_member.position.lower() != "manager":
            raise PermissionError("Only managers can remove movies.")
        if movie not in self.schedule:
            raise ValueError("Movie not found in schedule.")
        self.schedule.remove(movie)

    def remove_all_movies(self, staff):
        if not staff or staff.position.lower() != "manager":
            raise PermissionError("Only a manager can remove all movies.")
        self.schedule = []

    def choose_movies_to_play(self, staff_member, movies):
        if staff_member is None:
            raise ValueError("Staff member cannot be None.")
        if not isinstance(movies, list):
            raise ValueError("Movies must be provided as a list.")
        if staff_member.position.lower() != "manager":
            raise PermissionError("Only managers can choose movies to play.")
        for movie in movies:
            if movie is None:
                raise ValueError("Movie in selection cannot be None.")
            if movie not in self.schedule:
                self.schedule.append(movie)

    def list_movies(self):
        return [movie.title for movie in self.schedule]

    def has_movie(self, title):
        return any(movie.title == title for movie in self.schedule)

    def get_movie_by_title(self, title):
        if not title or not isinstance(title, str):
            raise ValueError("Invalid movie title.")
        for movie in self.schedule:
            if movie.title.lower() == title.lower():
                return movie
        raise ValueError("Movie titled '{}' not found.".format(title))

    def get_movies_by_genre(self, genre):
        if not genre:
            raise ValueError("Genre cannot be empty.")
        return [movie for movie in self.schedule
                if movie.genre.lower() == genre.lower()]

    def list_current_movies(self):
        return [movie.short_description() for movie in self.schedule]

    def get_movie_details(self):
        return "\n\n".join(str(movie) for movie in self.schedule)

    def clear_schedule(self):
        self.schedule = []

    def count_movies_by_genre(self):
        genres = {}
        for m in self.schedule:
            genres[m.genre] = genres.get(m.genre, 0) + 1
        return genres

    def remove_staff_member_by_name(self,
                                    first_name, last_name):
        self.staff = [s for s in self.staff
                      if not (s.first_name == first_name
                              and s.last_name == last_name)]

    def to_dict(self):
        return {
            "name": self.name,
            "address": self.address,
            "schedule": [movie.to_dict() for movie in self.schedule],
            "staff": [str(staff) for staff in self.staff]
        }

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            f.write(str(self))

    def save_to_json(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)  # type: ignore

    def export_schedule_to_json(self, filename):
        with open(filename, 'w') as f:
            json.dump([movie.to_dict() for movie
                       in self.schedule], f,  # type: ignore
                      indent=4)

    @staticmethod
    def read_from_json(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            cinema = Cinema(data['name'], data['address'])
            cinema.schedule = [
                Movie(
                    title=m['title'],
                    genre=m['genre'],
                    duration=m['duration'],
                    age_restriction=m['age_restriction'],
                    director=m['director'],
                    language=m['language'],
                    release_year=m['release_year'],
                    rating=m['rating'],
                    description=m['description']
                )
                for m in data.get('schedule', [])
            ]
            return cinema
