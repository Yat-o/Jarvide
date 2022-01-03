import copy

import disnake

from .dialogs import OpenView
from src.utils import EmbedFactory
from disnake.ext import commands, tasks


class Ide(commands.Cog):
    """Ide cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_commands = {}
        self.check_activity.start()

    @tasks.loop(seconds=0.001)
    async def check_activity(self):
        for channel in copy.copy(self.active_commands):
            for user in copy.copy(self.active_commands[channel]):
                message = self.bot.get_message(self.active_commands[channel][user])
                if all(child.disabled for child in message.components if isinstance(child, disnake.ui.Button)):
                    del self.active_commands[channel][user]

    @commands.command()
    async def ide(
        self, ctx: commands.Context, query: str = None, link: str = None
    ) -> None:
        if (
            ctx.channel in self.active_commands
            and ctx.author in self.active_commands[ctx.channel]
        ):
            return await ctx.send(
                "You already have an open ide in this channel! Press the `exit` button to make a new one!", 
                delete_after=15
            )

        embed = EmbedFactory.ide_embed(ctx, "File open: No file currently open")
        view = OpenView(ctx)
        view.bot_message = await ctx.send(
            embed=embed,
            view=view,
        )

        if ctx.channel not in self.active_commands:
            self.active_commands[ctx.channel] = {}

        self.active_commands[ctx.channel][ctx.author] = view.bot_message.id


def setup(bot: commands.Bot) -> None:
    """Setup Ide cog"""
    bot.add_cog(Ide(bot))
