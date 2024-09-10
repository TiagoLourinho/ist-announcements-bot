from dataclasses import dataclass

import requests
import xmltodict

from .announcement import Announcement, AnnouncementActions


@dataclass
class Course:
    """Defines a course"""

    link: str
    """ The link of the course fenix page """

    name: str = None
    """ The course name """

    years: str = None
    """ The course years """

    semester: str = None
    """ The course semester """

    announcements: list[Announcement] = None
    """ The list of announcements """

    def __post_init__(self):

        if not self.__is_link_valid(self.link):
            raise ValueError(
                "Invalid Fenix course link, should follow this format: https://fenix.tecnico.ulisboa.pt/disciplinas/XXXX/XXXX-XXXX/X-semestre"
            )

        # Link example:
        # https://fenix.tecnico.ulisboa.pt/disciplinas/XXXX/XXXX-XXXX/X-semestre

        parts = self.link.split("/")

        self.name = parts[4]
        self.years = parts[5]
        self.semester = parts[6]
        self.announcements = []

    def __is_link_valid(self, link: str) -> bool:
        """Checks if a link is valid"""

        # Correct link example:
        # https://fenix.tecnico.ulisboa.pt/disciplinas/XXXX/XXXX-XXXX/X-semestre

        start_string = "https://fenix.tecnico.ulisboa.pt/disciplinas/"
        end_string = "-semestre"

        # Check start and end string
        if not (link.startswith(start_string) and link.endswith(end_string)):
            return False

        # Find the "dynamic" parts, the course name, years etc
        start_idx = link.find(start_string) + len(start_string) + 1
        end_idx = link.find(end_string)

        parts = link[start_idx:end_idx].split("/")

        # The specific part should contain the course abbreviation, the academic year and semester
        if len(parts) != 3:
            return False

        course = parts[0]  # Can be anything basically
        years = parts[1].split("-")
        semester = parts[2]

        # Example: "2020-2021" and then split by "-"
        if len(years) != 2:
            return False

        # The years should both be ints and consecutive
        try:
            if int(years[1]) - int(years[0]) != 1:
                return False
        except:
            return False

        # Only 2 possible semesters
        if not (semester in ["1", "2"]):
            return False

        return True

    def __sort_announcements_by_date(
        self, announcements: list[Announcement]
    ) -> list[Announcement]:
        """Sorts the given announcement list by publication date"""

        return sorted(announcements, key=lambda announcement: announcement.pub_date)

    def __fetch_announcements_list(self) -> list[Announcement]:
        """Retrieves the announcements XML of a course and returns the list of announcements"""

        # Using Fenix API, see the example in https://fenixedu.org/dev/api/#get-coursesid
        url = f"https://fenix.tecnico.ulisboa.pt/disciplinas/{self.name}/{self.years}/{self.semester}/rss/announcement"

        response = requests.get(url)

        if response.status_code == 200:
            xml_data = response.text  # XML

            # Convert to dict and remove unnecessary info present in the original XML
            dict_data = xmltodict.parse(xml_data)
            announcements_list = dict_data["rss"]["channel"]["item"]

            # When there is only 1 announcement, the API returns just the announcement, instead of a list with just 1 element
            if isinstance(announcements_list, dict):
                announcements_list = [announcements_list]

            announcements = [
                Announcement(
                    title=announcement["title"],
                    description=announcement["description"],
                    link=announcement["link"],
                    author=announcement["author"],
                    pub_date=announcement["pubDate"],
                )
                for announcement in announcements_list
            ]

            return announcements

        else:
            raise Exception(
                f"Failed to retrieve XML. Status code: {response.status_code}"
            )

    def update_announcements(
        self,
    ) -> list[dict[str, Announcement | AnnouncementActions]]:
        """Fetches the latest announcements list and returns a dict with the changes to be used by the bot (each "change" contains the announcement and the action type)"""

        new_announcements = {
            announcement.id: announcement
            for announcement in self.__sort_announcements_by_date(
                self.__fetch_announcements_list()
            )
        }
        old_announcements = {
            announcement.id: announcement for announcement in self.announcements
        }

        # Keep track of the announcements added, deleted or updated
        changed = []
        get_dict = lambda announcement, action: {
            "announcement": announcement,
            "action": action,
        }

        # Search for added and updated announcements
        for id, announcement in new_announcements.items():
            if id in old_announcements:
                if (
                    old_announcements[id].title != new_announcements[id].title
                    or old_announcements[id].description
                    != new_announcements[id].description
                ):
                    # The id is the same, but the title or description changed, so the announcement was updated
                    changed.append(get_dict(announcement, AnnouncementActions.UPDATED))
                else:
                    # Nothing happened with the announcement (id, title and description remained the same)
                    pass
            else:
                # Not present in the old announcements list, so it is a new announcement
                changed.append(get_dict(announcement, AnnouncementActions.ADDED))

        # Search for deleted announcements
        for id, announcement in old_announcements.items():
            if id not in new_announcements:
                # Not present in the new announcements list so was deleted
                changed.append(get_dict(announcement, AnnouncementActions.DELETED))

        self.announcements = list(new_announcements.values())

        return changed
