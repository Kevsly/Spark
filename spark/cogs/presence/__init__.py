from spark.bot import Spark


async def setup(bot: Spark):
    from .core import Presence

    await bot.add_cog(Presence(bot))
