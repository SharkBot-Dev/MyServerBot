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

    @commands.hybrid_command(name="ping", description="Ping値を測定します。")
    @commands.cooldown(2, 5, type=commands.BucketType.user)
    async def ping(self, ctx: commands.Context):
        ws_latency_ms = self.bot.latency * 1000

        await ctx.send(f"Pong! {ws_latency_ms:.2f}ms")

async def setup(bot):
    await bot.add_cog(HelpCog(bot))