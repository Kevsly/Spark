from spark.bot import Spark


async def setup(bot: Spark):
    from .core import Core

    await bot.add_cog(Core(bot))
