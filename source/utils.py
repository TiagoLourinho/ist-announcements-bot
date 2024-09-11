""" Contains async utility functions """

import discord
from constants import CATEGORY_NAME
from discord import CategoryChannel, Guild, TextChannel
from models.announcement import Announcement, AnnouncementActions
from models.course import Course

#################### Async ####################


async def create_bot_category(guild: Guild) -> CategoryChannel:
    """Creates the bot category in the current `guild`"""

    category = discord.utils.get(guild.categories, name=CATEGORY_NAME)

    if category is None:
        category = await guild.create_category(CATEGORY_NAME)
        print(f"Category '{CATEGORY_NAME}' was created")
    else:
        print(f"Category '{CATEGORY_NAME}' already exists, skipping creation")

    return category


async def create_channel(
    guild: Guild, channel_name: str, allow_user_messages=False
) -> TextChannel:
    """Creates a channel with `channel_name` in the current `guild` (under the bot category)"""

    channel_name = format_channel_name(channel_name)

    category = discord.utils.get(guild.categories, name=CATEGORY_NAME)

    # Bot category didn't exist, create it
    if category is None:
        category = await create_bot_category(guild=guild)

    existing_channel = discord.utils.get(category.channels, name=channel_name)

    if existing_channel is None:

        # Set permissions of the channel
        # The bot will have an interactive channel and the rest are only informative so the user can't write there
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                send_messages=allow_user_messages,
                view_channel=True,
                read_message_history=True,
            ),
            guild.me: discord.PermissionOverwrite(send_messages=True),
        }

        existing_channel = await guild.create_text_channel(
            channel_name, category=category, overwrites=overwrites
        )
        print(f"Channel '{channel_name}' was created")
    else:
        print(f"Channel '{channel_name}' already exists, skipping creation")

    return existing_channel


async def delete_bot_category(guild: Guild):
    """Deletes the bot category and all the channels"""

    category = discord.utils.get(guild.categories, name=CATEGORY_NAME)

    if category is not None:

        for channel in category.channels:
            await channel.delete()

        await category.delete()
        print(f"Category '{CATEGORY_NAME}' was deleted")
    else:
        print(f"Category '{CATEGORY_NAME}' didn't exist, skipping deletion")


async def delete_channel(guild: Guild, channel_name: str) -> TextChannel:
    """Deletes a channel with `channel_name` in the current `guild` (under the bot category)"""

    channel_name = format_channel_name(channel_name)

    category = discord.utils.get(guild.categories, name=CATEGORY_NAME)

    if category is None:
        print(
            f"Category '{CATEGORY_NAME}' didn't exist, skipping channel '{channel_name}' deletion"
        )
        return

    existing_channel = discord.utils.get(category.channels, name=channel_name)

    if existing_channel is not None:
        await existing_channel.delete()
        print(f"Channel '{channel_name}' was deleted")
    else:
        print(f"Channel '{channel_name}' didn't exist, skipping deletion")


async def get_channel(guild: Guild, channel_name: str) -> TextChannel:
    """Returns the channel with `channel_name` inside the bot category"""

    channel_name = format_channel_name(channel_name)

    category = discord.utils.get(guild.categories, name=CATEGORY_NAME)

    if category is None:
        raise ValueError("Can't retrieve channel as category didn't exist.")

    existing_channel = discord.utils.get(category.channels, name=channel_name)

    if existing_channel is not None:
        return existing_channel
    else:
        raise ValueError(f"Can't retrieve channel as '{channel_name}' didn't exist.")


async def send_announcements_changes(
    channel: TextChannel, changes: list[dict[str, Announcement | AnnouncementActions]]
):
    """Send the messages informing the user of the latest changes in the announcements"""

    for change in changes:
        await channel.send(
            get_alert_message(
                announcement=change["announcement"], action=change["action"]
            )
        )


#################### Sync ####################


def format_channel_name(channel_name: str) -> str:
    """Formats the desired channel name to the name given by Discord"""

    return channel_name.replace(" ", "-").lower()


def get_init_message(course: Course) -> str:
    """Returns the formatted message for this course (used in the channel creation to display the course info)"""

    header = f"## **[{course.name} CHANNEL] - {course.semester.replace('-','º ')} of {course.years.replace('-','/')}**"

    course_link = f"[Click here to see the course page.]({course.link})"

    footer = f"-# Currently there are {len(course.announcements)} announcements in this course."

    return header + "\n\n" + course_link + "\n\n" + footer


def get_alert_message(announcement: Announcement, action: AnnouncementActions) -> str:
    """Returns the formatted message for this announcement and action"""

    header = f"## **[{action.name} ANNOUNCEMENT] - {announcement.title}**"

    footer = f"-# Published by {announcement.author} @ {announcement.pub_date.strftime('%H:%M of %A (%d/%m/%Y)')}."

    # Link doesn't make sense in the deleted action
    if action in (AnnouncementActions.ADDED, AnnouncementActions.UPDATED):
        footer += f" [Click here to see the announcement.]({announcement.link})"

    string = header + "\n\n" + announcement.description + "\n\n" + footer

    # Discord has a maximum message length of 2000 chars, so if it is exceeded don't display the description
    if len(string) > 2000:
        replacement = "*Description is too long to display.*"

        # Link doesn't make sense in the deleted action
        if action in (AnnouncementActions.ADDED, AnnouncementActions.UPDATED):
            replacement += (
                f" *Please check the [announcement on Fenix]({announcement.link}).*"
            )

        string = string.replace(
            announcement.description,
            replacement,
        )

    return string
