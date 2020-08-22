import discord
from discord.ext import commands
from prices import *

client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    print('Ready')


@client.command()
async def price(ctx, stock):
    await ctx.send(get_price(stock))

client.run('NzQ2ODQ2ODMzMDc4MzA0Nzk5.X0GRUA.uHNvXvmOgRg9fDtrT4h0vQc8KtI')