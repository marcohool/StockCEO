from bs4 import BeautifulSoup
from discord.ext import commands
import requests
import discord

class StockInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stats(self, ctx, stock: str):

        requestedStock = Stocks(stock)
        
        # Change colour of embed depending on performance
        try: 
            if requestedStock.performance[1][1] == "+":
                color = discord.Color(value=int("7EE622", 16))
            else:
                color = discord.Color(value=int("FF0000", 16))
        except Exception:
            await ctx.send("Please enter a valid stock symbol (e.g. TSLA)")
            return

        # Build embed
        embed = discord.Embed(title=(f"{requestedStock.stockName} | {requestedStock.currency}"), description = requestedStock.description, color = color)
        embed.add_field(name = "Current Price", value=(f"{requestedStock.price} {requestedStock.performance[1]}"), inline = True)
        embed.set_image(url="https://cdn.discordapp.com/attachments/746874886475087992/747242226559615026/unknown.png")
        await ctx.send(embed=embed)

class Stocks():

    def __init__(self, stockName):
        self.html = None
        self.stockName = self.searchSite(stockName)

        if (not self.stockName):
            stockName = stockName + ".l"
            self.stockName = self.searchSite(stockName)
            if (not self.stockName):
                return

        currency = self.html.find("div", {"C($tertiaryColor) Fz(12px)"}).text.split()
        self.currency = currency[len(currency)-1]
        self.price = self.html.find("span", {"Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text
        self.performance = self.getPerformance()
        self.description = self.getDescription(stockName)

    def searchSite(self, stockName):
        r = requests.get('https://finance.yahoo.com/quote/' + stockName + '/')
        self.html = BeautifulSoup(r.text, features='html.parser')

        try:
            return self.html.find('h1', {"D(ib) Fz(18px)"}).text
        except:
            return
    
    def getPerformance(self):
        try:
            return self.html.find("span", {"Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($positiveColor)"}).text.split()
        except Exception:
            return self.html.find("span", {"Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($negativeColor)"}).text.split()
    
    def getDescription(self, stockName):
        print(stockName)
        r = requests.get(f"https://uk.finance.yahoo.com/quote/{stockName}/profile?p={stockName}")
        self.html = BeautifulSoup(r.text, features='html.parser')
        desc = self.html.find_all("p", {"class":"Mt(15px) Lh(1.6)"})[0].text.strip().split(".")
        if (len(desc[0]) < 30):
            return (f"{desc[0]}. {desc[1]}.")
        return desc[0]+"."

 

def setup(bot):
    bot.add_cog(StockInfo(bot))