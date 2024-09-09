""" Contains the methods corresponding to bot events """

from .bot import bot


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}, starting up...")

    for guild in bot.guilds:
        print(f"Initializing guild '{guild.name}'")
