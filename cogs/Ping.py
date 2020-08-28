from discord.ext import commands
import time


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        before_ws = int(round(self.bot.latency * 1000, 1))
        await ctx.send(f"{before_ws}ms")


def setup(bot):
    bot.add_cog(Ping(bot))
