import discord
from discord.ext import commands
import logging
import glob

from libs.constant import TOKEN


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all(),
        )
        self.help_command = None

    async def setup_hook(self):
        await self.load_extension("jishaku")
        for path in glob.glob("cogs/**/*.py", recursive=True):
            await self.load_extension(path[:-3].replace("/", "."))
        await self.tree.sync()

    async def on_ready(self):
        logger = logging.getLogger("discord")
        logger.info(">> Bot is ready!")


if __name__ == "__main__":
    bot = MyBot()
    bot.run(token=TOKEN)
