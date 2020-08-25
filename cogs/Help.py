from discord.ext import commands
import discord


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(description=(
            "All bot comands are stated below"), color=discord.Color(value=int("36393f", 16)))
        embed.set_author(
            name="StockCEO", icon_url="https://cdn.discordapp.com/avatars/747147465735798914/20e537ad3284a9aa8fbc4cae81e9e236.png")
        embed.add_field(name=":chart_with_upwards_trend: Stocks",
                        value="`$stats [stock ticker]`, `$graph [stock ticker] [duration]`", inline=False)
        embed.add_field(name=":wrench: Other", value="`$ping`", inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.remove_command("help")
    bot.add_cog(Help(bot))
