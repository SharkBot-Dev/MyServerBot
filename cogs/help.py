from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()

        self.bot = bot

    @commands.hybrid_command(name="help", description="せんぞくぼっと！の使い方を表示します。")
    @commands.cooldown(2, 5, type=commands.BucketType.user)
    async def help(self, ctx: commands.Context):
        await ctx.send("""```
/help このメッセージを表示します。
/calc 計算をします。
/status 各ステータスを表示します。
```""")

async def setup(bot):
    await bot.add_cog(HelpCog(bot))