from bs4 import BeautifulSoup
from discord.ext import commands
from ruamel.yaml import YAML
import requests, discord, datetime, matplotlib as mpl, matplotlib.pyplot as plt



class StockInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stats(self, ctx, stock: str):

        requestedStock = Stocks(stock)

        Graph(requestedStock, 250).create_graph()

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
        # Get graph image
        file = discord.File("./graph.png", filename="graph.png")
        embed.set_image(url="attachment://graph.png")
        # Send embed
        await ctx.send(file=file, embed=embed)

class Stocks():

    def __init__(self, stockSymbol):
        self.html = None
        self.stockSymbol = stockSymbol
        self.stockName = self._searchSite()

        if (not self.stockName):
            self.stockSymbol = self.stockSymbol + ".l"
            self.stockName = self._searchSite()
            if (not self.stockName):
                return

        currency = self.html.find("div", {"C($tertiaryColor) Fz(12px)"}).text.split()
        self.currency = currency[len(currency)-1]
        self.price = self.html.find("span", {"Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text
        self.performance = self._getPerformance()
        self.description = self._getDescription()

    def _searchSite(self):
        r = requests.get('https://finance.yahoo.com/quote/' + self.stockSymbol + '/')
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
        r = requests.get(f"https://uk.finance.yahoo.com/quote/{self.stockSymbol}/profile?p={self.stockSymbol}")
        self.html = BeautifulSoup(r.text, features='html.parser')
        desc = self.html.find_all("p", {"class":"Mt(15px) Lh(1.6)"})[0].text.strip().split(".")
        if (len(desc[0]) < 30):
            return (f"{desc[0]}. {desc[1]}.")
        return desc[0]+"."
    
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

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # Get API key from config file 

        yaml = YAML()
        with open("./config.yml", "r", encoding="utf-8") as file:
            config = yaml.load(file)
        api_key = config["API-Key"]

        # Get list of prices 

        r = requests.get(f"http://api.marketstack.com/v1/eod?access_key={api_key}symbols={self.stock.getStockSymbol()}&limit={self.duration}")
        closing_prices = []
        price_dates = []
        json = r.json()
        data = json['data']
        for stock in data:
            if stock['date'] > dates[0]:
                closing_prices.append(stock['close'])
                price_dates.append(stock['date'][:10])

        # Reformat dates to 'day/month'

        def remove_zero(day):
            if day == '10' or day == '20' or day == '30':
                return day
            else:
                return day.replace('0', '')

        def reformat_date(date):
            day = remove_zero(date[8:10])
            month = months[int(remove_zero(date[5:7]))-1]
            return f"{day} {month}"

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
        plt.title(f'{self.duration} Day Performance', loc='center', fontweight="bold", fontname="lucida sans")
        plt.savefig('./graph.png', bbox_inches='tight', pad_inches=0.1)
        plt.close()
 

def setup(bot):
    bot.add_cog(StockInfo(bot))