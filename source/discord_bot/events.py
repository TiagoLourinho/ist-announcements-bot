""" Contains the methods corresponding to bot events """

from discord.ext import commands
from utils import create_bot_category, create_channel, delete_bot_category

from .bot import bot
from .tasks import update_announcements


@bot.event
async def on_ready():
    """Starts the bot and creates the channels"""

    print(f"Logged in as {bot.user}, starting up...")

    for guild in bot.guilds:

        # Clean up
        await delete_bot_category(guild)

        print(f"Initializing guild '{guild.name}'")

        # Create category and manage channel
        await create_bot_category(guild)
        channel = await create_channel(
            guild=guild, channel_name="Manage", allow_user_messages=True
        )

        # Display hello message and commands
        ctx = await bot.get_context(
            await channel.send("Hello! Ready to track the announcements...")
        )
        await bot.get_command("help").invoke(ctx)

    # Start the update announcements task
    if not update_announcements.is_running():
        update_announcements.start()


@bot.event
async def on_command_error(ctx, error):
    """Displays help message when there is an error"""

    if isinstance(error, commands.CheckFailure):
        return  # If there was a check failure nothing should be done, the bot just won't respond
    else:
        ctx = await bot.get_context(await ctx.send("Oops! Something wasn't right..."))
        await bot.get_command("help").invoke(ctx)
