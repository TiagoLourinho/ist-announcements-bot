""" Contains async utility functions """

import discord
import requests
import xmltodict
from constants import CATEGORY_NAME
from discord import CategoryChannel, Guild, TextChannel

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


async def create_channel(guild: Guild, channel_name: str) -> TextChannel:
    """Creates a channel with `channel_name` in the current `guild` (under the bot category)"""

    channel_name = format_channel_name(channel_name)

    category = discord.utils.get(guild.categories, name=CATEGORY_NAME)

    # Bot category didn't exist, create it
    if category is None:
        category = await create_bot_category(guild=guild)

    existing_channel = discord.utils.get(category.channels, name=channel_name)

    if existing_channel is None:
        existing_channel = await guild.create_text_channel(
            channel_name, category=category
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


#################### Sync ####################


def format_channel_name(channel_name: str) -> str:
    """Formats the desired channel name to the name given by Discord"""

    return channel_name.replace(" ", "-")


def get_announcements_list(url: str) -> list:
    """Retrieves the announcements XML of a course (given the `url`) and returns the list of announcements"""

    response = requests.get(url)

    if response.status_code == 200:
        xml_data = response.text

        dict_data = xmltodict.parse(xml_data)

        # Remove unnecessary info, returning only the announcements list
        return dict_data["rss"]["channel"]["item"]
    else:
        raise Exception(f"Failed to retrieve XML. Status code: {response.status_code}")
