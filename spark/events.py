import asyncio
import os

import discord
from discord.ext import commands

from spark import logger
from spark.bot import Spark
from spark.utils import chat_formatting as cf
from spark.utils.embeds import create_embed


def setup_events(bot: Spark):
    log = logger.root_logger.getChild("events")
    started = asyncio.Event()

    @bot.event
    async def on_ready():
        if started.is_set():
            return

        if "NO_SYNC_COMMANDS" not in os.environ:
            log.info("Syncing application commands with Discord...")
            try:
                SERVER_ID = os.environ["SERVER_ID"].split(", ")[0]  # noqa
                await bot.tree.sync(guild=discord.Object(id=SERVER_ID))
            except discord.HTTPException:
                log.exception("Failed to sync application commands.")

        started.set()

    @bot.event
    async def on_command_error(ctx: commands.Context, error: Exception) -> None:
        if (
            ctx.guild and not ctx.channel.permissions_for(ctx.me).send_messages
            or ctx.me.is_timed_out()
        ):
            return

        if hasattr(ctx.command, "on_error"):
            return

        if isinstance(error, commands.NotOwner):
            await ctx.send(cf.error("You are not the owner of the bot."), ephemeral=True)
            if ctx.guild:
                log.warning(
                    f"{ctx.author} (ID: {ctx.author.id}) tried to execute an owner only command in the guild "
                    f"{ctx.guild.name} (ID: {ctx.guild.id}), but the user is not an owner of the bot."
                )
            else:
                log.warning(
                    f"{ctx.author} (ID: {ctx.author.id}) tried to execute an owner only command in the bots DMs, "
                    f"but the user is not an owner of the bot."
                )
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(cf.error("This command doesn't seem to exist; did you spell it correctly?"), ephemeral=True)
        elif isinstance(error, commands.BadArgument):
            await ctx.send(embed=create_embed(
                description=error.args[0],
                color=discord.Color.red()
            ), ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=create_embed(
                description="You are missing the permission(s) `"
                            + ", ".join(error.missing_permissions)
                            + "` to execute this command!",
                color=discord.Color.red()
            ), ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(embed=create_embed(
                description="I am missing the permission(s) `"
                            + ", ".join(error.missing_permissions)
                            + "` to fully perform this command!",
                color=discord.Color.red()
            ), ephemeral=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(cf.error(str(error).capitalize()), ephemeral=True)
        else:
            raise error
