import os

from discord_bot.bot import bot
from discord_bot.events import on_ready  # Not used but needs to be imported to register
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
