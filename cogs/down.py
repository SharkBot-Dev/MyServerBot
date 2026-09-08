from discord.ext import commands, tasks
import discord

STATUS_EMOJIS = {
    discord.Status.online: "<:online:1407922300535181423>",
    discord.Status.idle: "<:idle:1407922295711727729>",
    discord.Status.dnd: "<:dnd:1407922294130741348>",
    discord.Status.offline: "<:offline:1407922298563854496>",
}

class DownCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()

        self.bot = bot

    @commands.Cog.listener(name="on_presence_update")
    async def on_presence_update_bot_down(self, before: discord.Member, after: discord.Member):
        if after.guild.id != 1343124570131009579:
            return

        if after.id == 1322100616369147924:
            if after.status == discord.Status.offline:
                await self.bot.get_channel(1361173338763956284).send(embed=discord.Embed(title=f"Botがダウンしました。", color=discord.Color.red()).add_field(name="Bot名", value=after.name).set_thumbnail(url=after.display_avatar.url))
        elif after.id == 1392853908879179936:
            if after.status == discord.Status.offline:
                await self.bot.get_channel(1361173338763956284).send(embed=discord.Embed(title=f"Botがダウンしました。", color=discord.Color.red()).add_field(name="Bot名", value=after.name).set_thumbnail(url=after.display_avatar.url))

    @tasks.loop(minutes=10)
    async def status_presence(self):
        await self.bot.change_presence(activity=discord.CustomActivity(name="/help | 専属Bot"))

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        self.status_presence.start()

    @commands.hybrid_command(name="status", description="各Botのステータスを表示します。")
    @commands.cooldown(2, 5, type=commands.BucketType.user)
    async def status(self, ctx: commands.Context):
        guild = self.bot.get_guild(1343124570131009579)
        bots = [guild.get_member(1322100616369147924), guild.get_member(1343156909242454038), guild.get_member(1502156877998460959), guild.get_member(1537386704137363527), guild.get_member(1537996178157871154)]
        status_text = "\n".join([f"{STATUS_EMOJIS.get(b.status)} {b.name}" for b in bots])
        await ctx.send(embed=discord.Embed(title="各Botのステータス", description=status_text, color=discord.Color.green()))

async def setup(bot):
    await bot.add_cog(DownCog(bot))