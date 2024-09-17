""" Contains the bot scheduled tasks """

from constants import MANAGE_CHANNEL, UPDATE_INTERVAL
from discord.ext import tasks
from utils import get_channel

from .bot import bot, db


@tasks.loop(minutes=UPDATE_INTERVAL)
async def update_announcements():
    """Updates the announcements on every guild"""

    for guild in bot.guilds:
        if len(db.get_courses_list(guild)) > 0:  # Skip if no courses are being tracked
            channel = await get_channel(guild=guild, channel_name=MANAGE_CHANNEL)
            ctx = await bot.get_context(
                await channel.send("Triggering automatic update...")
            )
            await bot.get_command("update").invoke(ctx)

    db.save_backup()
