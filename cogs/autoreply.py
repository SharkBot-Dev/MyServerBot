from discord.ext import commands
import discord

class AutoReplyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.THREAD_MORE_CHANNEL_ID = 1528992425991733349
        self.BUG_CHANNEL_ID = 1490227625883467826
        self.NEW_CHANNEL_ID = 1352823275469799464
        self.REPORT_CHANNEL_ID = 1485859712212668547

    @commands.Cog.listener(name="on_thread_create")
    async def on_thread_create_message(self, thread: discord.Thread):
        if thread.parent_id == self.THREAD_MORE_CHANNEL_ID:
            message = await thread.send(embed=discord.Embed(title="スレッド作成の際のお知らせ", color=discord.Color.blue(), description="<#1344231915607035914> に違反している内容の場合、\nサーバー管理者により処罰、\nそしてスレッドの削除が行われます。\nあらかじめご了承ください。"))
            await message.add_reaction("✅️")
        elif thread.parent_id == self.BUG_CHANNEL_ID:
            message = await thread.send(embed=discord.Embed(title="バグ報告ありがとうございます。", color=discord.Color.purple(), description="管理者および、サブ管理者、\nそして開発者が対応しますので、\nしばらくお待ちください。"))
            await message.add_reaction("👍")
        elif thread.parent_id == self.NEW_CHANNEL_ID:
            message = await thread.send(embed=discord.Embed(title="ご提案ありがとうございます。", color=discord.Color.green(), description="この提案内容は、\n必ずしも採用されるわけではありません。\nご了承ください。"), view=discord.ui.View(timeout=None).add_item(discord.ui.Button(emoji="✅", label="採用", style=discord.ButtonStyle.green, custom_id="new_ok")).add_item(discord.ui.Button(emoji="❌", label="不採用", style=discord.ButtonStyle.red, custom_id="new_no")))
            await message.add_reaction("✅")
        elif thread.parent_id == self.REPORT_CHANNEL_ID:
            message = await thread.send(embed=discord.Embed(title="ご報告ありがとうございます。", color=discord.Color.red(), description="この通報内容は、管理者やモデレーターによって議論され、\n処罰、もしくは警告などが決定します。").set_footer(text="不適切な通報やデマ等の場合は、通報者が処罰されます。"))
            await message.add_reaction("✅")

    @commands.Cog.listener(name="on_interaction")
    async def on_interaction_new(self, interaction: discord.Interaction):
        try:
            if interaction.data["component_type"] == 2:
                try:
                    custom_id = interaction.data["custom_id"]
                except:
                    return
                if interaction.user.id != 1335428061541437531:
                    return
                if "new_ok" == custom_id:
                    await interaction.response.send_message(embed=discord.Embed(title="この案は採用されました。", color=discord.Color.green()))
                elif "new_no" == custom_id:
                    await interaction.response.send_message(embed=discord.Embed(title="この案は否決されました。", color=discord.Color.red()))
        except:
            return

async def setup(bot):
    await bot.add_cog(AutoReplyCog(bot))