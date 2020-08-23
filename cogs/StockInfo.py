from bs4 import BeautifulSoup
from discord.ext import commands
import requests

class StockInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def price(self, ctx, stock: str):
        r = requests.get('https://finance.yahoo.com/quote/' + stock + '/')
        html = BeautifulSoup(r.text, features='html.parser')
        price = html.find_all('div', {"My(6px) Pos(r) smartphone_Mt(6px)"})[0].find("span").text
        await ctx.send("$"+price)

def setup(bot):
    bot.add_cog(StockInfo(bot))