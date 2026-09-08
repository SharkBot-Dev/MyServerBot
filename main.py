import asyncio

import discord
from discord.ext import commands, tasks
import os
import dotenv
import aiohttp
import re

dotenv.load_dotenv()

bot = commands.Bot(command_prefix=["s.", "dd!"], intents=discord.Intents.all(), help_command=None)

@bot.event
async def setup_hook() -> None:
    await bot.load_extension("cogs.down")
    await bot.load_extension("cogs.emojis")
    await bot.load_extension("cogs.owner")
    await bot.load_extension("cogs.math")
    await bot.load_extension("cogs.help")
    await bot.load_extension("cogs.autoreply")

    await bot.load_extension("jishaku")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.channel.id == 1523851417713115157:
        await message.delete()
        return

    await bot.process_commands(message)

bot.run(os.environ.get('TOKEN'))