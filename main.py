import asyncio

import discord
from discord.ext import commands, tasks
import os
import dotenv
import aiohttp

dotenv.load_dotenv()

STATUS_EMOJIS = {
    discord.Status.online: "<:online:1407922300535181423>",
    discord.Status.idle: "<:idle:1407922295711727729>",
    discord.Status.dnd: "<:dnd:1407922294130741348>",
    discord.Status.offline: "<:offline:1407922298563854496>",
}

bot = commands.Bot(command_prefix="dd!", intents=discord.Intents.all(), help_command=None)

@tasks.loop(minutes=10)
async def status_presence():
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.head("https://status.sharkbot.xyz/status/default") as response:
                if response.status == 200:
                    await bot.change_presence(activity=discord.CustomActivity(name="サービスは起動しています！", emoji="✅"))
                else:
                    await bot.change_presence(activity=discord.CustomActivity(name="サービスは現在ダウン中です..", emoji="❌"))
    except aiohttp.ClientConnectorError:
        await bot.change_presence(activity=discord.CustomActivity(name="サービスは現在ダウン中です..", emoji="❌"))
    except asyncio.TimeoutError:
        await bot.change_presence(activity=discord.CustomActivity(name="サービスは現在ダウン中です..", emoji="❌"))

@bot.event
async def on_ready():
    status_presence.start()

@bot.event
async def on_automod_action(execution: discord.AutoModAction):
    try:
        await execution.channel.send(embed=discord.Embed(title="ルール違反を検知しました！", description="繰り返される場合はBan処理を行います。", color=discord.Color.red()).set_footer(text="このメッセージは3分後に削除されます。"), content=f"<@{execution.user_id}>", delete_after=180)
    except:
        return
    
@bot.event
async def on_guild_emojis_update(guild: discord.Guild, before, after):
    try:
        if guild.id == 1343124570131009579:
            emoji = list(set(after) - set(before))[0]
            channel = bot.get_channel(1418169887062360084)
            await channel.send(embed=discord.Embed(description=str(emoji), title="新しい絵文字が作成されたよ！使ってみよう！", color=discord.Color.green()))
    except:
        return

@bot.event
async def on_presence_update(before: discord.Member, after: discord.Member):
    if after.id == 1322100616369147924:
        if after.status == discord.Status.offline:
            await bot.get_channel(1361173338763956284).send(embed=discord.Embed(title=f"SharkBotがダウンしました。", color=discord.Color.red()))
    elif after.id == 1392853908879179936:
        if after.status == discord.Status.offline:
            await bot.get_channel(1361173338763956284).send(embed=discord.Embed(title=f"SharkBotがダウンしました。", color=discord.Color.red()))

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    await bot.process_commands(message)

@bot.command()
@commands.is_owner()
async def echo(ctx: commands.Context, text: str):
    await ctx.channel.send(text)
    await ctx.message.delete()
    
@bot.command()
@commands.is_owner()
async def embed(ctx: commands.Context, *, text: str):
    await ctx.channel.send(embed=discord.Embed(description=text))
    await ctx.message.delete()

@bot.command()
@commands.is_owner()
async def status(ctx: commands.Context):
    bots = [ctx.guild.get_member(1322100616369147924), ctx.guild.get_member(1392853908879179936)]
    status_text = "\n".join([f"{STATUS_EMOJIS.get(b.status)} {b.name}" for b in bots])
    await ctx.channel.send(embed=discord.Embed(title="各Botのステータス", description=status_text, color=discord.Color.blue()))

bot.run(os.environ.get('TOKEN'))