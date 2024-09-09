""" Contains the commands the bot answers to """

from .bot import bot


@bot.command()
async def help(ctx):

    help_text = """
**Bot Commands:**

`$help` 
- *See this message.*

`$tracked` 
- *Returns the list of the courses being tracked in this server.*

`$add <course_link>` 
- *Starts tracking the announcements of the course defined by `course_link`.* 
- *The link should be the home page link of the course like:*

`https://fenix.tecnico.ulisboa.pt/disciplinas/XXXX/XXXX-XXXX/X-semestre`

`$remove <course_name>` 
- *Stops tracking the announcements of the course with `course_name`.* 
- *The name should be the same name used in the output of `$tracked`.*
"""

    await ctx.send(help_text)
