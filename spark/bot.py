import os
from datetime import datetime
from enum import IntEnum

from discord.ext import commands

from spark import logger


class ExitCode(IntEnum):
    NORMAL = 0
    FATAL_ERROR = 1
    CONFIG_ERROR = 38


# noinspection PyTypeChecker
class Spark(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            command_prefix=commands.when_mentioned_or("s?"),
            owner_ids=[*map(int, os.environ["SPARK_OWNERS"].split(", "))],
            *args,
            **kwargs
        )
        self.log = logger.root_logger
        self.uptime: datetime | None = None
        self._exit_code: int = ExitCode.NORMAL
        self.get_command("help").hidden = True

    async def setup_hook(self):
        from spark.cogs import LOAD_EXTS

        self.uptime = datetime.utcnow()

        for ext in LOAD_EXTS:
            try:
                self.log.info("Loading extension: %s", ext)
                await self.load_extension(ext)
            except Exception as e:
                self.log.error("Failed to load extension %r", ext, exc_info=e)
        self.log.info("----------------------------------------------")

    # async def prefixes(self, _, message: discord.Message) -> list[str]:
    #     """Get command prefixes for a given command invocation."""
    #     await self.wait_until_ready()
    #     prefixes = self.bot_config.prefixes
    #     if message.guild:
    #         guild: db.Guild | None = await handler.get_guild(self.log, message.guild)
    #         if not guild:
    #             return [f"<@{self.user.id}> ", f"<@!{self.user.id}> "]
    #         prefixes = guild and guild.prefixes or prefixes
    #     return deduplicate([f"<@{self.user.id}> ", f"<@!{self.user.id}> ", *prefixes])