from datetime import datetime
from typing import Optional, Any, Union

import discord
from discord import Colour

CHECK = "<:check:1278189910863646803>"
EMBED_FOOTER_ICON = "https://i.imgur.com/SaUbJoD.png"


def create_embed(
    title: Optional[Any] = None,
    description: Optional[Any] = None,
    colour: Optional[Union[int, Colour]] = None,
    color: Optional[Union[int, Colour]] = None,
    footer_text: Optional[Any] = None,
    thumbnail: Optional[Any] = None,
    url: Optional[Any] = None,
    timestamp: Optional[datetime] = None,
) -> discord.Embed:
    """Wrapper around discord.Embed, allowing you to provide footer_text or thumbnails instantly."""
    embed = discord.Embed(
        title=title,
        description=description,
        colour=colour if colour is not None else color if color is not None else discord.Color.blue(),
        url=url,
        timestamp=timestamp
    )
    embed.set_footer(
        text=footer_text or f"by @kevsly",
        icon_url=EMBED_FOOTER_ICON
    )

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    return embed
