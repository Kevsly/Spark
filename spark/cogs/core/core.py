import discord
from discord.ext import commands

from spark.bot import Spark
from spark.cogs.predicates import private
from spark.utils.embeds import create_embed


class Core(commands.Cog, name="Core"):
    def __init__(self, bot: Spark):
        super().__init__()
        self.bot = bot
        self.log = bot.log

    # region Ping Command

    @commands.hybrid_command(name="ping")
    @commands.is_owner()
    @private()
    async def ping(self, ctx: commands.Context):
        """Get the current latency of the bot to Discord."""
        await ctx.defer(ephemeral=True)

        latency_ms = round(self.bot.latency * 1000)
        color = (
            discord.Colour.red()
            if latency_ms >= 300
            else discord.Colour.yellow()
            if latency_ms >= 150
            else discord.Colour.green()
        )

        await ctx.send(embed=create_embed(
            title="\N{TABLE TENNIS PADDLE AND BALL} Pong!",
            description=f"The bot latency is `{latency_ms}ms`",
            color=color
        ))

    # endregion

    # region Embed Command

    @commands.hybrid_command(name="embed")
    @commands.check(lambda ctx: ctx.interaction is not None)
    @commands.is_owner()
    @private()
    async def embed(self, ctx: commands.Context, description: str, title: str = None):
        """Send messages in embed format."""
        await ctx.defer(ephemeral=True)

        await ctx.channel.get_partial_message(ctx.message.id).delete()
        await ctx.send(embed=create_embed(
            title=title,
            description=description
        ))

    # endregion
