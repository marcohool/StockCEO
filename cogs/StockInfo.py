from bs4 import BeautifulSoup
from discord.ext import commands
from ruamel.yaml import YAML
import requests
import discord
import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt


class StockInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stats(self, ctx, stock: str):

        requestedStock = Stocks(stock, ctx)

        if (not await requestedStock._checkValidStock()):
            return

        # Creates graph as graph.png and returns colour depending on past month performance of the stock
        colour = Graph(requestedStock, 30).create_graph()

        # Build embed
        embed = discord.Embed(title=(f"{requestedStock.stockName} | {requestedStock.currency}"),
                              description=requestedStock.description, color=discord.Color(value=int(colour, 16)))
        embed.add_field(name="Current Price", value=(
            f"{requestedStock.price} {requestedStock.performance[1]}"), inline=True)
        # Get graph image
        file = discord.File("./graph.png", filename="graph.png")
        embed.set_image(url="attachment://graph.png")
        # Send embed
        await ctx.send(file=file, embed=embed)

    @commands.command()
    async def graph(self, ctx, stock: str, timePeriod: str):
        requestedStock = Stocks(stock, ctx)

        if (not await requestedStock.checkValidStock()):
            return

        colour = Graph(requestedStock, int(timePeriod)).create_graph()

        embed = discord.Embed(
            title=(f"{requestedStock.stockName} | {requestedStock.currency}"), color=discord.Color(value=int(colour, 16)))
        file = discord.File("./graph.png", filename="graph.png")
        embed.set_image(url="attachment://graph.png")
        await ctx.send(file=file, embed=embed)


class Stocks():

    def __init__(self, stockSymbol, ctx):
        self.html = None
        self.stockSymbol = stockSymbol
        self.stockName = self._searchSiteWithTicker()
        self.ctx = ctx

        if (not self.stockName):
            self.stockSymbol = self.stockSymbol + ".l"
            self.stockName = self._searchSiteWithTicker()
            if (not self.stockName):
                return

        currency = self.html.find(
            "div", {"C($tertiaryColor) Fz(12px)"}).text.split()
        self.currency = currency[len(currency)-1]
        self.price = self.html.find(
            "span", {"Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text
        self.performance = self._getPerformance()
        self.description = self._getDescription()

    def _searchSiteWithTicker(self):
        r = requests.get('https://finance.yahoo.com/quote/' +
                         self.stockSymbol + '/')
        self.html = BeautifulSoup(r.text, features='html.parser')

        try:
            return self.html.find('h1', {"D(ib) Fz(18px)"}).text
        except:
            return

    def _getPerformance(self):
        try:
            return self.html.find("span", {"Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($positiveColor)"}).text.split()
        except Exception:
            return self.html.find("span", {"Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($negativeColor)"}).text.split()

    def _getDescription(self):
        r = requests.get(
            f"https://uk.finance.yahoo.com/quote/{self.stockSymbol}/profile?p={self.stockSymbol}")
        self.html = BeautifulSoup(r.text, features='html.parser')
        try:
            desc = self.html.find_all("p", {"class": "Mt(15px) Lh(1.6)"})[
                0].text.strip().split(".")
        except Exception:
            return
        if (len(desc[0]) < 30):
            return (f"{desc[0]}. {desc[1]}.")
        return desc[0]+"."

    async def checkValidStock(self):
        # If requestedStock.price doens't exist then stock ticker was wrong
        try:
            self.price
            return True
        except Exception:
            await self.ctx.send("Please enter a valid ticker symbol (e.g. TSLA, GOOGL, AAPL)")
            return False

    def getStockSymbol(self):
        return self.stockSymbol


class Graph():

    def __init__(self, stock, duration):
        self.stock = stock
        self.duration = duration

    def create_graph(self):
        today = datetime.date.today()
        dates = []
        for x in range(-self.duration, 0):
            day = (today + datetime.timedelta(days=x)).strftime('%Y-%m-%d')
            dates.append(day)

        yaml = YAML()
        with open("./config.yml", "r", encoding="utf-8") as file:
            config = yaml.load(file)
        api_key = config["API-Key"]

        # Get list of prices

        r = requests.get(
            f"http://api.marketstack.com/v1/eod?access_key={api_key}symbols={self.stock.getStockSymbol()}&limit={self.duration}")
        closing_prices = []
        price_dates = []
        json = r.json()
        data = json['data']
        for stock in data:
            if stock['date'] > dates[0]:
                closing_prices.append(stock['close'])
                price_dates.append(stock['date'][:10])

        closing_prices = closing_prices[::-1]
        price_dates = price_dates[::-1]

        length = len(closing_prices)

        # Create ticks list
        ticks = (0, length // 4, length // 2, (length // 4) * 3,  length - 1)

        mpl.rcParams['axes.spines.right'] = False
        mpl.rcParams['axes.spines.top'] = False
        mpl.rcParams['axes.spines.left'] = False
        plt.rcParams['ytick.left'] = False
        plt.rcParams['axes.facecolor'] = '2f3136'
        plt.rcParams['axes.edgecolor'] = 'white'
        plt.rcParams['figure.facecolor'] = '2f3136'
        plt.rcParams['text.color'] = 'white'
        plt.rcParams['axes.labelcolor'] = 'white'
        plt.rcParams['ytick.color'] = 'white'
        plt.rcParams['xtick.color'] = 'white'
        plt.plot(price_dates, closing_prices, color='green')
        plt.xticks(ticks)
        plt.grid(True, which='major', axis='y', linestyle='--')
        plt.title(f'{self.duration} Day Performance', loc='center',
                  fontweight="bold", fontname="lucida sans")
        plt.savefig('./graph.png', bbox_inches='tight', pad_inches=0.1)
        plt.close()

        final_price = closing_prices[-1]
        first_price = closing_prices[0]

        if final_price >= first_price:
            return "7EE622"
        else:
            return "FF0000"


def setup(bot):
    bot.add_cog(StockInfo(bot))
