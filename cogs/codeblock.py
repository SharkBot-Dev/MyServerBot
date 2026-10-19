import re

import aiohttp
import discord
from discord.ext import commands, tasks

codeblock_py_pattern = re.compile(r"```py\n.*```", flags=re.DOTALL)

class CodeblockCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()

        self.bot = bot

        self.ALLOW_CHANNEL_IDS = [1459778013301571666]

    @commands.Cog.listener(name="on_message")
    async def on_message_codeblock_make(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id not in self.ALLOW_CHANNEL_IDS:
            return

        codeblock_py = codeblock_py_pattern.search(message.content)
        if codeblock_py:
            await message.channel.send(embed=discord.Embed(title="Pythonコードを検出しました。", description=codeblock_py.group(0)))

async def setup(bot):
    await bot.add_cog(CodeblockCog(bot))