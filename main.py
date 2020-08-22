import discord
from discord.ext import commands
from prices import get_price
from ruamel.yaml import YAML

yaml = YAML()

with open("./config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)

bot = commands.Bot(command_prefix=config["Prefix"], description="Stock information bot")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name = config["Watching Status"]))


@bot.command()
async def price(ctx, stock):
    await ctx.send(get_price(stock))

bot.run(config["Token"])