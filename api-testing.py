import requests
import matplotlib as  mpl
import matplotlib.pyplot as plt
import datetime

# make list of last 30 days
today = datetime.date.today()
dates = []
for x in range(-30, 0):
    day = (today + datetime.timedelta(days=x)).strftime('%Y-%m-%d')
    dates.append(day)

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# getting list of prices (last 30 days in this case)
r = requests.get('http://api.marketstack.com/v1/eod?access_key=&symbols=AAPL&limit=30')
closing_prices = []
price_dates = []
json = r.json()
data = json['data']
for stock in data:
    if stock['date'] > dates[0]:
        closing_prices.append(stock['close'])
        price_dates.append(stock['date'][:10])

# reformat dates to 'day month'
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
price_dates = [reformat_date(date) for date in price_dates]

#create ticks list
ticks = []
index = len(closing_prices)-1
while index > 0:
    ticks.append(index)
    index -= 3

ticks = tuple(ticks)

mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False
plt.rcParams['axes.facecolor'] = '2f3136'
plt.rcParams['axes.edgecolor'] = 'white'
plt.rcParams['figure.facecolor'] = '2f3136'
plt.rcParams['text.color'] = 'white'
plt.rcParams['axes.labelcolor'] = 'white'
mpl.rcParams['xtick.color'] = 'white'
mpl.rcParams['ytick.color'] = 'white'

plt.plot(price_dates, closing_prices, color='green')
plt.xticks(ticks)
plt.grid(True, which='major', axis='y', linestyle='--')
plt.title('30 Day Performance', loc='center', fontweight="bold", fontname="lucida sans")
plt.savefig('./example.png', bbox_inches='tight', pad_inches=0.1)


