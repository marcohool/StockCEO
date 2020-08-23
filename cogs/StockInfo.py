from bs4 import BeautifulSoup
from discord.ext import commands
import requests
import discord

class StockInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stats(self, ctx, stock: str):
        r = requests.get('https://finance.yahoo.com/quote/' + stock + '/')
        html = BeautifulSoup(r.text, features='html.parser')

        try:
            performance = html.find("span", {"Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($positiveColor)"}).text
        except Exception:
            try:
                performance = html.find("span", {"Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($negativeColor)"}).text
            except Exception:
                await ctx.send("Please enter a valid stock symbol (e.g. TSLA)")
                return
        
        price = html.find('span', {"Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text
        currency = html.find("div", {"C($tertiaryColor) Fz(12px)"}).text
        correctCurrency = currency.split()


        name = html.find('h1', {"D(ib) Fz(18px)"}).text
        performanceSplit = performance.split()

        if performanceSplit[1][1] == "+":
            color = discord.Color(value=int("7EE622", 16))
        else:
            color = discord.Color(value=int("FF0000", 16))
        
        embed = discord.Embed(title=(f"{name} | {correctCurrency[len(correctCurrency)-1]}"), description = (f"{price} {performanceSplit[1]}"), color = color)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(StockInfo(bot))