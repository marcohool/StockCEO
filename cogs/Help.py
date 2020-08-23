from discord.ext import commands
import discord

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(description = ("All bot comands are stated below"), color = discord.Color(value=int("36393f", 16)))
        embed.set_author(name="StockCEO", icon_url="https://cdn.shopify.com/s/files/1/1061/1924/products/Money_Emoji_Icon_59b7293e-e703-4ba4-b3c3-a7b9401f89fb_large.png?v=1571606091")
        embed.add_field(name=":chart_with_upwards_trend: Stocks", value = "`$price [stock symbol]`", inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.remove_command("help")
    bot.add_cog(Help(bot))