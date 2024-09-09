import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True  # So the bot can read commands

bot = commands.Bot(command_prefix="$", intents=intents)
