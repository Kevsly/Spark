import itertools
import re

import discord
from discord.ext import commands
from discord.ext.commands import DefaultHelpCommand, Paginator
from jishaku.paginators import PaginatorEmbedInterface as _PaginatorEmbedInterface

SINGLE_LINE_BREAK = re.compile(r"(?<!\n)\n(?!\n)")


# This is used on every command docstring; this can be suppressed by adding
# ``extras={"single_linebr": True}`` to the command decorator
def replace_single_linebr(string: str) -> str:
    return SINGLE_LINE_BREAK.sub(" ", string)


class PaginatorEmbedInterface(_PaginatorEmbedInterface):
    def __init__(self, *args, ending_note: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.ending_note = ending_note

    @property
    def send_kwargs(self) -> dict:
        display_page = self.display_page
        self._embed.description = self.pages[display_page]
        self._embed.set_footer(
            text="Page {current}/{total} | {ending_note}".format(
                ending_note=self.ending_note.replace("\n", " "),
                current=display_page + 1,
                total=self.page_count
            )
        )
        return {"embed": self._embed}


class SparkHelpCommand(DefaultHelpCommand):
    context: commands.Context

    def __init__(self):
        super().__init__(
            paginator=Paginator(max_size=1985, prefix="", suffix=""),
            commands_heading="Commands:",
            no_category="No Category",
            show_parameter_descriptions=False,
        )

    @property
    def clean_prefix(self):
        return self.context.clean_prefix

    def get_ending_note(self):
        return (
            "Type '{prefix}help <command>' for more info on a command. "
            "You can also type '{prefix}help <category>' for more info on a category."
        ).format(prefix=self.clean_prefix)

    async def send_pages(self):
        destination = self.get_destination()

        interface = PaginatorEmbedInterface(
            self.context.bot,
            self.paginator,
            owner=self.context.author,
            embed=discord.Embed(color=discord.Color.blue()).set_author(  # noqa
                name="Help Docs for {bot}".format(bot=self.context.bot.user.name),
                icon_url=self.context.bot.user.display_avatar.with_static_format("png"),
            ),
            ending_note=self.get_ending_note(),
            timeout=60,
        )
        await interface.send_to(destination)

    def add_command_formatting(self, command):
        if command.description:
            desc = replace_single_linebr(
                command.description.replace("[p]", self.context.clean_prefix)
            )
            self.paginator.add_line(desc, empty=True)

        signature = self.get_command_signature(command)
        self.paginator.add_line(
            "**Usage:** `{signature}`".format(signature=signature.rstrip()), empty=True
        )

        if command.help and (
            # Allow disabling removing single line breaks for cases where we need finer control
            # over how a command's help output is displayed; mostly meant to be used wherever
            # we use FlagConverter
            chelp := command.help
            if command.extras.get("single_linebr")
            else replace_single_linebr(command.help)
        ):
            try:
                self.paginator.add_line(chelp.replace("[p]", self.context.clean_prefix), empty=True)
            except RuntimeError:
                for line in chelp.splitlines():
                    self.paginator.add_line(line)
                self.paginator.add_line()

    def add_indented_commands(self, commands, *, heading, max_size=None):
        if not commands:
            return

        self.paginator.add_line(f"### __**{heading}**__" if heading else heading)
        max_size = max_size or self.get_max_size(commands)

        get_width = discord.utils._string_width
        for command in commands:
            name = command.name
            width = max_size - (get_width(name) - len(name))
            entry = (
                f'\N{ZERO WIDTH SPACE}{self.indent * " "}**`{name:<{width}}`** {command.short_doc}'
            )
            self.paginator.add_line(self.shorten_text(entry))

    async def send_group_help(self, group):
        self.add_command_formatting(group)

        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        self.add_indented_commands(filtered, heading=self.commands_heading)

        await self.send_pages()

    async def send_cog_help(self, cog):
        if cog.description:
            self.paginator.add_line(replace_single_linebr(cog.description), empty=True)

        filtered = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)
        self.add_indented_commands(filtered, heading=self.commands_heading)

        await self.send_pages()

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        if bot.description:
            # <description> portion
            self.paginator.add_line(bot.description, empty=True)

        no_category = f"\u200b{self.no_category}:"

        # noinspection PyShadowingNames
        def get_category(command, *, no_category=no_category):
            cog = command.cog
            return f"{cog.qualified_name}:" if cog is not None else no_category

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)  # noqa
        max_size = self.get_max_size(filtered)
        to_iterate = itertools.groupby(filtered, key=get_category)

        # Now we can add the commands to the page.
        for category, cmds in to_iterate:
            cmds = sorted(cmds, key=lambda c: c.name) if self.sort_commands else list(cmds)
            self.add_indented_commands(cmds, heading=category, max_size=max_size)  # noqa
            self.paginator.add_line()

        await self.send_pages()