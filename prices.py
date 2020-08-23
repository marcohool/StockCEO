from bs4 import BeautifulSoup
import requests

def get_price(stock):
    r = requests.get('https://finance.yahoo.com/quote/' + stock + '/')
    html = BeautifulSoup(r.text, features='html.parser')
    price = html.find_all('div', {"My(6px) Pos(r) smartphone_Mt(6px)"})[0].find("span").text
    return "$"+price