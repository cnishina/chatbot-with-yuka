import os
import asyncio
from dotenv import load_dotenv
from twitchio.ext import commands
from focus import write_focus


load_dotenv()
_ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


class Bot(commands.Bot):
    def __init__(self):
        # Initialize our Bot with our access token, prefix and a list of
        # channels to join on boot...
        super().__init__(
            token=_ACCESS_TOKEN,
            prefix="!",
            initial_channels=["bedtimebear_808"],
        )

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")

    @commands.command()
    async def focus(self, ctx: commands.Context):
        author = ctx.message.author.name
        message = ctx.message.content.replace("!focus ", "").strip()
        timestamp = ctx.message.timestamp
        write_focus(author, message, timestamp)
        await ctx.send(f"{author} is focusing: {message}.")
