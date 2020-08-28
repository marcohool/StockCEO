import discord
import os
from discord.ext import commands
from ruamel.yaml import YAML

yaml = YAML()

with open("./config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)

bot = commands.Bot(
    command_prefix=config["Prefix"], description="Stock information bot")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=config["Watching Status"]))

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

try:
    bot.run(config["Token"])
except Exception as e:
    print(f"Fatal error: {e}")