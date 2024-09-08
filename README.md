# IST Announcements Bot

## What is it?

Announcements in Fenix require the student to manually check each course for new announcements or updates, so this is a Discord bot that does both and notifies the student automatically.

## How can I add the bot to a server?

Just click [here](https://discord.com/oauth2/authorize?client_id=1282121445983649792&permissions=2064&integration_type=0&scope=bot).

## How can I replicate the bot creation process?

Follow these steps:

1. Create a discord server.
2. Create the discord application in the [developer portal](https://discord.com/developers/applications).
3. Go to `Bot` and turn on `Message Content Intent`.
4. Extract the token by clicking on `Reset Token` and create a `.env` file in the root folder of the project with the token. For example: `BOT_TOKEN="SOME_TOKEN_HERE"`.
5. Go to `OAuth2`, then on `OAuth2 URL Generator` select `bot`. Now, in `Bot Permissions` select: `Manage Channels` and `Send Messages`. Finally, copy and paste the generated URL on the browser, adding the bot to the desired server.
6. Run `main.py` after activating the virtual environment with `pipenv`.
