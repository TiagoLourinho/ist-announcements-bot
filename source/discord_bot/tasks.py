""" Contains the bot scheduled tasks """

import time

from constants import MANAGE_CHANNEL, UPDATE_INTERVAL
from discord.ext import tasks
from utils import get_channel

from .bot import bot, db

LAST_UPDATE = None


@tasks.loop(minutes=UPDATE_INTERVAL)
async def update_announcements():
    """Updates the announcements on every guild"""

    global LAST_UPDATE

    current_time = time.time()
    update_interval_in_seconds = UPDATE_INTERVAL * 60

    if (
        LAST_UPDATE is not None
        and current_time - LAST_UPDATE < update_interval_in_seconds
    ):
        # Since this bot is running as a service, when it is shutdown during the night it will try to "make up"
        # for the missed checks after restarting, so if "too close" to the last check time just return
        return

    LAST_UPDATE = current_time

    for guild in bot.guilds:
        if len(db.get_courses_list(guild)) > 0:  # Skip if no courses are being tracked
            channel = await get_channel(guild=guild, channel_name=MANAGE_CHANNEL)
            ctx = await bot.get_context(
                await channel.send("Triggering automatic update...")
            )
            await bot.get_command("update").invoke(ctx)

    db.save_backup()
