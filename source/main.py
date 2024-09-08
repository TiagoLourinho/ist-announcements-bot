import os

from bot import bot
from dotenv import load_dotenv
from events import on_ready

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
