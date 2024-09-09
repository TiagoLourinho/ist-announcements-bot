""" Contains the methods corresponding to bot events """

from utils import create_bot_category, create_channel, delete_bot_category

from .bot import bot


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}, starting up...")

    for guild in bot.guilds:

        # Clean up
        await delete_bot_category(guild)

        print(f"Initializing guild '{guild.name}'")

        await create_bot_category(guild)

        await create_channel(
            guild=guild, channel_name="Manage", allow_user_messages=True
        )
