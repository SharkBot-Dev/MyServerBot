from discord.ext import commands
import discord

class AutoReplyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.THREAD_MORE_CHANNEL_ID = 1528992425991733349

    @commands.Cog.listener(name="on_thread_create")
    async def on_thread_create_message(self, thread: discord.Thread):
        if thread.parent_id == self.THREAD_MORE_CHANNEL_ID:
            message = await thread.send(embed=discord.Embed(title="スレッド作成の際のお知らせ", color=discord.Color.blue(), description="<#1344231915607035914> に違反している内容の場合、\nサーバー管理者により処罰、\nそしてスレッドの削除が行われます。\nあらかじめご了承ください。"))
            await message.add_reaction("✅️")

async def setup(bot):
    await bot.add_cog(AutoReplyCog(bot))