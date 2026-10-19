import re

import aiohttp
import discord
from discord.ext import commands, tasks

ipv4_pattern = re.compile(
    r"^("
    r"(25[0-5]|"  # 250-255
    r"2[0-4][0-9]|"  # 200-249
    r"1[0-9]{2}|"  # 100-199
    r"[1-9][0-9]|"  # 10-99
    r"[0-9])"  # 0-9
    r"\.){3}"  # 繰り返し: 3回ドット付き
    r"(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])"  # 最後のオクテット
    r"$"
)

class NetworkCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()

        self.bot = bot

    @commands.hybrid_command(name="iplookup", description="IPアドレスの詳細を表示します。")
    @commands.cooldown(2, 5, type=commands.BucketType.user)
    async def iplookup(self, ctx: commands.Context, ipアドレス: str):
        if ipv4_pattern.match(ipアドレス):
            await ctx.defer()

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://ip-api.com/json/{ipアドレス}?lang=ja"
                ) as response:
                    try:
                        js = await response.json()

                        embed = discord.Embed(title=f"{ipアドレス}の情報", color=discord.Color.green())
                        embed.add_field(name="国名", value=js.get("country", "不明"))
                        embed.add_field(name="都市名", value=js.get("city", "不明"))
                        embed.add_field(name="プロバイダ", value=js.get("isp", "不明"))
                        embed.add_field(name="緯度", value=js.get("lat", "不明"))
                        embed.add_field(name="経度", value=js.get("lon", "不明"))
                        embed.add_field(
                            name="タイムゾーン", value=js.get("timezone", "不明")
                        )

                        await ctx.reply(embed=embed)
                    except:
                        await ctx.reply(content="APIのレートリミットです。")
                        return
        else:
            return await ctx.reply("無効なIPアドレスです。")

async def setup(bot):
    await bot.add_cog(NetworkCog(bot))