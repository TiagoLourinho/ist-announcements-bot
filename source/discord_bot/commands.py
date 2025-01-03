""" Contains the commands the bot answers to """

from datetime import datetime
from functools import wraps

from constants import CATEGORY_NAME, MANAGE_CHANNEL, UPDATE_INTERVAL
from discord.ext import commands
from utils import (
    create_channel,
    delete_channel,
    get_channel,
    get_init_message,
    send_announcements_changes,
)

from .bot import bot, db

# Flag to avoid running multiple commands at the same time
processing_command = False


def handle_processing_flag(func):
    """Decorator to set/unset the flag while running a command"""

    @wraps(func)
    async def wrapper(ctx, *args, **kwargs):
        global processing_command

        if processing_command:
            await ctx.send("I'm already processing another command. Please wait.")
            return

        processing_command = True
        try:
            return await func(ctx, *args, **kwargs)
        finally:
            processing_command = False

    return wrapper


def should_answer_command(ctx):
    """Checks if the bot should answer the command"""
    return (
        ctx.channel.category
        and ctx.channel.category.name
        == CATEGORY_NAME  # Should be inside the bot category
        and ctx.channel.name == MANAGE_CHANNEL  # and on the manage channel
    )


@bot.command()
@commands.check(should_answer_command)
@handle_processing_flag
async def help(ctx):
    """Displays bot commands"""

    help_text = f"""
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

`$update` 
- *Triggers a manual update of the announcements (they update automatically every {UPDATE_INTERVAL} minutes).*
"""

    await ctx.send(help_text)


@bot.command()
@commands.check(should_answer_command)
@handle_processing_flag
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
@commands.check(should_answer_command)
@handle_processing_flag
async def add(ctx, course_link: str):
    """Adds a course"""

    try:

        # Add course and create course channel
        course = db.add_course(guild=ctx.guild, course_link=course_link)
        await ctx.send("Adding course...")
        channel = await create_channel(guild=ctx.guild, channel_name=course.name)

        # Get the announcements changes and send the messages
        changes = course.update_announcements()
        await channel.send(
            get_init_message(course)
        )  # Done after the update (otherwise the length of the announcements list will be 0)
        await send_announcements_changes(channel=channel, changes=changes)

        await ctx.send("Course added. Check the new channel with the announcements.")

    except Exception as e:
        await ctx.send(e)
    finally:
        db.save_backup()


@bot.command()
@commands.check(should_answer_command)
@handle_processing_flag
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
    finally:
        db.save_backup()


@bot.command()
@commands.check(should_answer_command)
@handle_processing_flag
async def update(ctx):
    """Updates the announcements of each course"""

    n_changes = 0
    for course in db.get_courses_list(guild=ctx.guild):

        changes = course.update_announcements()
        await send_announcements_changes(
            channel=await get_channel(guild=ctx.guild, channel_name=course.name),
            changes=changes,
        )

        n_changes += len(changes)

    manage_channel = await get_channel(guild=ctx.guild, channel_name=MANAGE_CHANNEL)
    await manage_channel.send(
        f"Updated announcements @ {datetime.now().strftime('%H:%M of %d/%m/%Y')} **({n_changes} changes)**"
    )
