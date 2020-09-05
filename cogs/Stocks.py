from bs4 import BeautifulSoup
from discord.ext import commands
from ruamel.yaml import YAML
import requests
import discord
import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import mysql.connector


class StockInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stats(self, ctx, stock: str):

        requestedStock = Stocks(stock, ctx)

        if (not await requestedStock.checkValidStock()):
            return

        # Creates graph as graph.png and returns colour depending on past month performance of the stock
        colour = Graph(requestedStock, 30).create_graph()

        # Build embed
        embed = discord.Embed(title=(f"{requestedStock.stockName} | {requestedStock.currency}"),
                              description=requestedStock.description, color=discord.Color(value=int(colour, 16)))
        embed.add_field(name="Current Price", value=(
            f"{requestedStock.getPrice()} {requestedStock.getPerformance()[1]}"), inline=True)
        embed.add_field(name="Day's Range", value=requestedStock.getDayRange(), inline=True)
        embed.add_field(name="Previous Close", value=requestedStock.getPreviousClose(), inline=True)
        embed.add_field(name="Market Cap", value=requestedStock.getMarketCap(), inline=True)   
        embed.add_field(name="52 Week Range", value=requestedStock.get52WeekRange(), inline=True)
        embed.add_field(name="Open", value=requestedStock.getOpen(), inline=True)

        # Get graph image
        file = discord.File("./graph.png", filename="graph.png")
        embed.set_image(url="attachment://graph.png")
        # Send embed
        await ctx.send(file=file, embed=embed)

    @commands.command()
    async def graph(self, ctx, stock: str, timePeriod: str):

        requestedStock = Stocks(stock, ctx)

        # If stock isn't valid, don't excecute
        if (not await requestedStock.checkValidStock()):
            return

        timePeriodEnding = timePeriod[len(timePeriod) - 1]

        if (timePeriodEnding == "m"):
            timePeriod = int(timePeriod[:-1])
            timePeriod = timePeriod * 30
        elif (timePeriodEnding == "y"):
            timePeriod = int(timePeriod[:-1])
            if (timePeriod > 1):
                await ctx.send("Please enter a duration between 7 days (7d) and 1 year (1y)")
                return
            timePeriod = timePeriod * 365
        elif (timePeriodEnding == "w"):
            timePeriod = int(timePeriod[:-1])
            timePeriod = timePeriod * 7
        else:
            if (timePeriodEnding == "d"):
                timePeriod = int(timePeriod[:-1])
            try:
                if (int(timePeriod) < 7):
                    await ctx.send("Please enter a duration between `7 days (7d)` and `1 year (1y)`")
                    return
            except Exception:
                await ctx.send("""Please follow the format: `$graph [ticker symbol] [duration]` \n\nFor example: `$graph AAPL 6m`.
                                 Please note we can only provide graphs for the duration of the past 1 week and 1 year""")
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
        self.valid = True
        self.stockName = self._searchSiteWithTicker()
        self.ctx = ctx

        if (not self.valid):
            self.stockSymbol = self.stockSymbol + ".l"
            self._searchSiteWithTicker()
            if (not self.valid):
                return

        self._getSummaryItems()
        currency = self.html.find(
            "div", {"C($tertiaryColor) Fz(12px)"}).text.split()
        self.currency = currency[len(currency) - 1]
        self.price = self.html.find(
            "span", {"Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text
        self.performance = self._getPerformance()
        self.description = self._getDescription()

    def _searchSiteWithTicker(self):
        r = requests.get(f'https://finance.yahoo.com/quote/{self.stockSymbol}')
        self.html = BeautifulSoup(r.text, features='html.parser')

        try:
            return self.html.find('h1', {"D(ib) Fz(18px)"}).text
        except Exception:
            self.valid = False

    def _getSummaryItems(self):
        allSummaryItems = []
        table = self.html.find_all('table')
        for row in table[0].find_all("tr"):
            for cell in row.findAll("td")[1::2]:
                allSummaryItems.append(cell.text)

        for row in table[1].find_all("tr"):
            for cell in row.findAll("td")[1::2]:
                allSummaryItems.append(cell.text)

        # Previous Close, Open, Bid, Ask, Day's Range, 52 Week Range, Volume, Avg.Volume, Market Cap, Beta (5Y Monthly), PE Ration etc

        self.previousClose = allSummaryItems[0]
        self.open = allSummaryItems[1]
        self.dayRange = allSummaryItems[4]
        self.week52Range = allSummaryItems[5]
        self.marketCap = allSummaryItems[8]

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
        return desc[0] + "."

    async def checkValidStock(self):

        if (not self.valid):
            await self.ctx.send("Please enter a valid ticker symbol (e.g. TSLA, GOOGL, AAPL)")
        return self.valid

    def getStockSymbol(self):
        return self.stockSymbol

    def getPrice(self):
        return self.price

    def getStockName(self):
        return self.stockName

    def getCurrency(self):
        return self.currency

    def getPerformance(self):
        return self.performance
    
    def getPreviousClose(self):
        return self.previousClose
    
    def getOpen(self):
        return self.open

    def getDayRange(self):
        return self.dayRange

    def get52WeekRange(self):
        return self.week52Range

    def getMarketCap(self):
        return self.marketCap


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
        ticks = (0, length // 4, length // 2, (length // 4) * 3, length - 1)

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


class StockAlert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def addAlert(self, ctx, stock: str, difference: str):

        requestedStock = Stocks(stock, ctx)

        # If stock isn't valid, don't excecute
        if (not await requestedStock.checkValidStock()):
            return

        try:
            differenceRaw = int(difference)
        except Exception:
            try:
                differenceRaw = int(difference[:-1])
            except Exception:
                await ctx.send("Please follow the format: `$addalert [stock ticker] [% change]`.\n\n For example: `$addalert TSLA -10%`.")
                return

        if (differenceRaw > 50 or differenceRaw < -50):
            await ctx.send("Please set a difference between -50% and +50%")
            return

        targetValue = float(requestedStock.getPrice().replace(
            ",", "")) * (1 + int(differenceRaw) / 100)

        if differenceRaw < 0:
            targetValue = targetValue * -1

        success = DBConnection.Instance().insertAlert(requestedStock.getStockSymbol(),
                                                      targetValue, ctx.channel.id, ctx.guild.id, ctx.author.id)

        if (success):
            await ctx.send("There was an error with adding the alert")
        else:
            await ctx.send("Alert successfuly added :white_check_mark:")

    @commands.command()
    async def viewAlerts(self, ctx):

        DBConnection.Instance().searchAlerts(ctx.author.id)

        rs = DBConnection.Instance().getCursor()

        if (rs.fetchall() == []):
            await ctx.send("You don't have any alerts set! You can add alerts by using the command `$addalert [stock ticker] [% change]`")
            return

        message = f"**Current alerts for {ctx.author.mention}**\n\n"

        for row in rs:
            requestedStock = Stocks(row[1], ctx)
            message = message + \
                f"**{requestedStock.getStockName()}**: {row[2]} {requestedStock.getCurrency()}\n"

        message = message + "\nYou will be tagged in the channel you created the alert when the above stocks reach their respective value."

        await ctx.send(message)


class Singleton:
    def __init__(self, cls):
        self._cls = cls

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError("Singleton must be accessed through Instance()")

    def __instancecheck(self, inst):
        return isinstance(inst, self._cls)


@ Singleton
class DBConnection(object):
    def __init__(self):

        yaml = YAML()

        with open("./config.yml", "r", encoding="utf-8") as file:
            config = yaml.load(file)

        try:
            self.conn = mysql.connector.connect(
                host=config["DB-Server"],
                user=config["DB-Username"],
                password=config["DB-Password"]
                print("Conn successfull !")
            )
        except Exception as e:
            raise ConnectionError("Database connection failed ", e)

    def insertAlert(self, stockTicker, targetPrice, channelID, guildID, userID):

        sql = f"""INSERT INTO sql2362237.tbl_GuildChannels(
            GuildID, ChannelID)
            VALUES ({guildID}, {channelID})"""

        status = self.execute(sql)

        if (not status):
            return False

        sql = f"""INSERT INTO sql2362237.tbl_Alerts(
            StockTicker, TargetPrice, UserID, GuildChannelID)
            VALUES ('{stockTicker}', {targetPrice}, {userID}, {self.cursor.lastrowid})"""

        status = self.execute(sql)

        if (not status):
            return False

    def searchAlerts(self, authorID):

        sql = f"SELECT * FROM sql2362237.tbl_Alerts WHERE UserID = '{authorID}'"

        self.execute(sql)

    def execute(self, sql):
        try:
            self.cursor = self.conn.cursor(buffered=True)
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except Exception as e:
            print(e)
            self.conn.rollback()
            return False

    def __str__(self):
        return "Database connection object"

    def getConn(self):
        return self.conn

    def getCursor(self):
        return self.cursor


def setup(bot):
    bot.add_cog(StockInfo(bot))
    bot.add_cog(StockAlert(bot))
