import os
import pickle

from discord import Guild

from .course import Course


class Database:
    """
    This class stores data related to the bot operation
    and acts as an interface in case it is upgraded to an actual database in the future
    """

    __BACKUP_FILE = "db.pkl"

    def __init__(self) -> None:

        # The data contains the list of courses being tracked per each guild
        # (The dict is indexed using the guild ID)
        self.__data: dict[int, list[Course]] = dict()

    def add_course(self, guild: Guild, course_link: str) -> Course:
        """Adds a course to a guild"""

        if guild.id not in self.__data:
            self.__data[guild.id] = []

        # Check if this course already exists
        for course in self.__data[guild.id]:
            if course.link == course_link:
                raise ValueError("This course is already being tracked.")

        course = Course(link=course_link)
        self.__data[guild.id].append(course)

        return course

    def remove_course(self, guild: Guild, course_name: str):
        """Removes a course from a guild"""

        if guild.id not in self.__data:
            raise ValueError(f"Server {guild.name} isn't using the bot.")

        temp = [
            course for course in self.__data[guild.id] if course.name != course_name
        ]

        # If the length is the same no element was removed
        if len(temp) == len(self.__data[guild.id]):
            raise ValueError("This course doesn't exist.")
        else:
            self.__data[guild.id] = temp

    def get_courses_list(self, guild: Guild) -> list[Course]:
        """Returns the list of courses being tracked"""

        return self.__data[guild.id] if guild.id in self.__data else []

    def save_backup(self):
        """Saves a backup of the database in a file"""

        with open(self.__BACKUP_FILE, "wb") as backup_file:
            pickle.dump(self.__data, backup_file)

    def try_load_backup(self):
        """Tries to load a backup of the database (returns a boolean representing whether it was successful or not)"""

        if os.path.exists(self.__BACKUP_FILE):
            with open(self.__BACKUP_FILE, "rb") as backup_file:
                self.__data = pickle.load(backup_file)
                return True
        else:
            return False
