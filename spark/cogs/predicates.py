import os

from discord.ext import commands

server_ids_str = os.getenv("SERVER_ID", "")
SERVER_IDS = {int(sid) for sid in server_ids_str.split(", ") if sid.isdigit()}


def private():
    def predicate(ctx):
        return ctx.guild and ctx.guild.id in SERVER_IDS
    return commands.check(predicate)
