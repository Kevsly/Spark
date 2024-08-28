import random

import discord
from discord.ext import commands, tasks

from spark.cogs.predicates import private
from spark.utils import chat_formatting as cf


class Presence(commands.Cog, name="Presence"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.log = bot.log.getChild("cogs.presence")
        self.presence_task.start()

    def cog_unload(self) -> None:
        self.presence_task.cancel()

    @commands.hybrid_command("presencesync")
    @commands.is_owner()
    @private()
    async def presence_sync(self, ctx: commands.Context):
        """Sync the bot's presence."""
        try:
            self.presence_task.restart()
            await ctx.send(cf.success("My presence is synchronized."))
        except Exception as e:
            self.log.error("Encountered an unexpected error while syncing the bot's presence.", exc_info=e)
            await ctx.send(cf.error("Failed to synchronize presence."))

    async def update_presence(self):
        try:
            if random.randint(1, 1000) == 777:
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Kev's Bad Code"))
                return

            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Rain Drops | s?help"))
        except Exception as e:
            self.log.error("Encountered an unexpected error while changing the bot's presence.", exc_info=e)

    @tasks.loop(hours=1)
    async def presence_task(self):
        try:
            await self.update_presence()
        except Exception as e:
            self.log.error("Encountered an unexpected error while updating the bot's presence.", exc_info=e)

    @presence_task.before_loop
    async def before_presence_task(self):
        await self.bot.wait_until_ready()
