import html
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto

from bs4 import BeautifulSoup


class AnnouncementActions(Enum):
    """The type of possible operations in announcements"""

    ADDED = auto()
    DELETED = auto()
    UPDATED = auto()


@dataclass
class Announcement:
    """Contains the announcement information"""

    title: str
    """ The title of the announcement """

    description: str
    """ The announcement itself """

    link: str
    """ The link to see the announcement """

    author: str
    """ The author of the announcement """

    pub_date: str | datetime  # A str is received and then converted to datetime
    """ The publication date """

    id: str = None
    """ The ID of the announcement """

    def __post_init__(self):

        # In Fenix the description and title can be updated but the publication date remains the same so
        # use the publication date as the ID for now.
        # Precision goes to the second so that should be enough to uniquely identify an announcement inside a course.
        # (An uuid isn't used because then it wouldn't be possible to use the ID to compare with the new announcements fetched)
        self.id = self.pub_date

        # Convert to a datetime object. Received date example: Tue, 22 Jul 2014 20:32:41 +0100
        self.pub_date = datetime.strptime(self.pub_date, "%a, %d %b %Y %H:%M:%S %z")

        # Remove the email, keeping only the author name. Received author example: XYZ@email.pt (XYZ)
        self.author = self.author[self.author.find("(") + 1 : self.author.rfind(")")]

        # Remove the HTML tags from the description (unescaping first as the initial contains encoded HTML tags)
        self.description = BeautifulSoup(
            html.unescape(self.description), "lxml"
        ).get_text(separator="\n")
