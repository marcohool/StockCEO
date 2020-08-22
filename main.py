import discord
from discord.ext import commands
from prices import *

bot = commands.Bot(command_prefix="!", description="Stock information bot")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name = "over 100 stocks!"))


@bot.command()
async def price(ctx, stock):
    await ctx.send(get_price(stock))

bot.run('NzQ2ODQ2ODMzMDc4MzA0Nzk5.X0GRUA.uHNvXvmOgRg9fDtrT4h0vQc8KtI')