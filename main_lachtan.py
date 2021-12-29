import discord
import os
from discord.ext import commands
from main import keep_alive

intents = discord.Intents().all()

bot = commands.Bot(intents=intents, command_prefix='!', help_command=None)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

keep_alive()
bot.run(os.getenv('TOKEN'))
