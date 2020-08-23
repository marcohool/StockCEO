from bs4 import BeautifulSoup
from discord.ext import commands
import requests
import discord

class StockInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def price(self, ctx, stock: str):
        r = requests.get('https://finance.yahoo.com/quote/' + stock + '/')
        html = BeautifulSoup(r.text, features='html.parser')
        price = html.find('span', {"Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text
        performance = html.find("span", {"Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($positiveColor)"}).text
        name = html.find('h1', {"D(ib) Fz(18px)"}).text

        embed = discord.Embed(title=name, description = (f"${price} {performance[7:]}"))

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(StockInfo(bot))