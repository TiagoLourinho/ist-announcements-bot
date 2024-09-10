""" Contains the commands the bot answers to """

from constants import CATEGORY_NAME, MANAGE_CHANNEL
from discord.ext import commands
from utils import (
    create_channel,
    delete_channel,
    get_init_message,
    send_announcements_changes,
)

from .bot import bot, db


def in_allowed_category(ctx):
    """Checks if the bot should answer (only if inside the bot category)"""
    return (
        ctx.channel.category
        and ctx.channel.category.name == CATEGORY_NAME
        and ctx.channel.name == MANAGE_CHANNEL
    )


@bot.command()
@commands.check(in_allowed_category)
async def help(ctx):
    """Displays bot commands"""

    help_text = """
**My Commands:**

`$help` 
- *See this message.*

`$tracked` 
- *Returns the list of the courses being tracked in this server.*

`$add <course_link>` 
- *Starts tracking the announcements of the course defined by `course_link`.* 
- *The link should be the home page link of the course like:*

https://fenix.tecnico.ulisboa.pt/disciplinas/XXXX/XXXX-XXXX/X-semestre

`$remove <course_name>` 
- *Stops tracking the announcements of the course with `course_name`.* 
- *The name should be the same name used in the output of `$tracked`.*
"""

    await ctx.send(help_text)


@bot.command()
@commands.check(in_allowed_category)
async def tracked(ctx):
    """Display the current tracked courses"""

    courses = db.get_courses_list(ctx.guild)

    if len(courses) == 0:
        await ctx.send(
            "Currently there aren't any courses being tracked. Add some using `$add`."
        )
    else:
        text = "**Courses being tracked:**\n" + "\n".join(
            [f"- {course.name}" for course in courses]
        )

        await ctx.send(text)


@bot.command()
@commands.check(in_allowed_category)
async def add(ctx, course_link: str):
    """Adds a course"""

    try:

        # Add course and create course channel
        course = db.add_course(guild=ctx.guild, course_link=course_link)
        await ctx.send("Adding course...")
        channel = await create_channel(guild=ctx.guild, channel_name=course.name)

        # Get the announcements changes and send the messages
        changes = course.update_announcements()
        await channel.send(get_init_message(course))
        await send_announcements_changes(channel=channel, changes=changes)

        await ctx.send("Course added. Check the new channel with the announcements.")

    except Exception as e:
        await ctx.send(e)


@bot.command()
@commands.check(in_allowed_category)
async def remove(ctx, course_name: str):
    """Removes a course"""

    try:

        # Removes a course and deletes course channel
        db.remove_course(guild=ctx.guild, course_name=course_name)
        await ctx.send("Removing course...")
        await delete_channel(guild=ctx.guild, channel_name=course_name)

        await ctx.send("Course removed.")

    except Exception as e:
        await ctx.send(str(e) + "\n")

        await bot.get_command("tracked").invoke(ctx)
