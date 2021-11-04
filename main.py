import configparser

import discord
import motor.motor_asyncio
from discord.ext import commands

initial_extensions = ['cogs.reminders']

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=['!'], intents=intents)

config = configparser.ConfigParser()
config.read('config.ini')
MONGO_TOKEN = config['MONGODB']['token']
DISCORD_TOKEN = config['DISCORD']['token']

database_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_TOKEN)
bot.database = database_client['TheBuds']

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

    bot.run(DISCORD_TOKEN)

