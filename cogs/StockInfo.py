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
        currency = html.find("div", {"C($tertiaryColor) Fz(12px)"}).text

        if (currency.endswith("USD")):
            currencySymbol = "$"
        elif (currency.endswith("GBp")):
            currencySymbol = "£"
            price = float(price)/100
        elif (currency.endswith("EUR")):
            currencySymbol = "€"

        try:
            performance = html.find("span", {"Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($positiveColor)"}).text
        except Exception:
            performance = html.find("span", {"Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($negativeColor)"}).text

        name = html.find('h1', {"D(ib) Fz(18px)"}).text

        performanceSplit = performance.split()

        if performanceSplit[1][1] == "+":
            color = discord.Color(value=int("7EE622", 16))
        else:
            color = discord.Color(value=int("FF0000", 16))
        
        embed = discord.Embed(title=name, description = (f"{currencySymbol}{price} {performanceSplit[1]}"), color = color)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(StockInfo(bot))