from discord.ext import commands, tasks
import discord

class EmojisCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()

        self.bot = bot

    @commands.Cog.listener(name="on_guild_emojis_update")
    async def on_guild_emojis_update_newemoji(self, guild: discord.Guild, before, after):
        try:
            if guild.id == 1343124570131009579:
                emoji = list(set(after) - set(before))[0]
                channel = self.bot.get_channel(1418169887062360084)
                await channel.send(str(emoji))
        except:
            return

async def setup(bot):
    await bot.add_cog(EmojisCog(bot))