import discord
from discord.ext import commands
from discord.ext.commands import Context as CommandContext

from query import parse


class StreamCog(object):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    async def stream(self, ctx: CommandContext, *, to_eval):
        val = parse(to_eval,
                    guild=ctx.guild,
                    channel=ctx.channel,
                    author=ctx.author,
                    bot=self.bot,
                    client=self.bot,
                    discord=discord,
                    )
        await ctx.send(repr(val))


def setup(bot: commands.Bot):
    bot.add_cog(StreamCog(bot))
