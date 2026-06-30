import asyncio

import discord
from discord.ext import commands, tasks
import os
import dotenv
import aiohttp
import re

from tags import Parser

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
async def on_guild_emojis_update(guild: discord.Guild, before, after):
    try:
        if guild.id == 1343124570131009579:
            emoji = list(set(after) - set(before))[0]
            channel = bot.get_channel(1418169887062360084)
            await channel.send(str(emoji))
    except:
        return

@bot.event
async def on_presence_update(before: discord.Member, after: discord.Member):
    if after.guild.id != 1343124570131009579:
        return

    if after.id == 1322100616369147924:
        if after.status == discord.Status.offline:
            await bot.get_channel(1361173338763956284).send(embed=discord.Embed(title=f"Botがダウンしました。", color=discord.Color.red()).add_field(name="Bot名", value=after.global_name).set_thumbnail(url=after.display_avatar.url))
    elif after.id == 1392853908879179936:
        if after.status == discord.Status.offline:
            await bot.get_channel(1361173338763956284).send(embed=discord.Embed(title=f"Botがダウンしました。", color=discord.Color.red()).add_field(name="Bot名", value=after.global_name).set_thumbnail(url=after.display_avatar.url))

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
async def eval(ctx: commands.Context, *, text: str):
    parser = Parser({
        "bot_id": str(bot.user.id),
        "author": ctx.author.display_name,
        "author_id": str(ctx.author.id),
        "author_avatar": str(ctx.author.display_avatar.key),
        "author_avatar_url": str(ctx.author.display_avatar.url),
        "author_mention": ctx.author.mention,
        "guild_id": str(ctx.guild.id),
        "guild_name": ctx.guild.name,
        "guild_icon": str(ctx.guild.icon.key) if ctx.guild.icon else "",
        "guild_icon_url": ctx.guild.icon.url if ctx.guild.icon else "",
        "count": str(ctx.guild.member_count),
        "channel_name": str(ctx.channel.name),
        "channel_id": str(ctx.channel.id),
        "message_id": str(ctx.message.id)
    })
    await ctx.channel.send(await parser.parse(text))
    await ctx.message.add_reaction("✅")

@bot.command()
@commands.cooldown(2, 5, type=commands.BucketType.user)
async def status(ctx: commands.Context):
    bots = [ctx.guild.get_member(1322100616369147924), ctx.guild.get_member(1392853908879179936)]
    status_text = "\n".join([f"{STATUS_EMOJIS.get(b.status)} {b.name}" for b in bots])
    await ctx.channel.send(embed=discord.Embed(title="各Botのステータス", description=status_text, color=discord.Color.blue()))

@bot.command()
@commands.cooldown(2, 5, type=commands.BucketType.user)
async def help(ctx: commands.Context):
    await ctx.channel.send(embed=discord.Embed(title="せんぞくぼっと！の使い方", description="`dd!status`で各Botのステータスを確認します。\n`dd!calc <計算式>`で計算します。", color=discord.Color.green()))

@bot.command()
@commands.cooldown(2, 5, type=commands.BucketType.user)
async def calc(ctx: commands.Context, *, expression: str):
    def safe_calculate(expression):
        if not re.fullmatch(r'[0-9+\-*/().\s]+', expression):
            return "計算エラー"

        try:
            tokens = re.findall(r'\d*\.\d+|\d+|[+\-*/()]', expression)
                
            ops = [] 
            values = []
            precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

            def apply_op():
                if len(values) < 2: return
                b = values.pop()
                a = values.pop()
                op = ops.pop()
                if op == '+': values.append(a + b)
                if op == '-': values.append(a - b)
                if op == '*': values.append(a * b)
                if op == '/': 
                    if b == 0: raise ZeroDivisionError
                    values.append(a / b)

            for token in tokens:
                if token.replace('.', '', 1).isdigit():
                    values.append(float(token))
                elif token == '(':
                    ops.append(token)
                elif token == ')':
                    while ops and ops[-1] != '(':
                        apply_op()
                    ops.pop()
                else:
                    while ops and ops[-1] in precedence and precedence[ops[-1]] >= precedence[token]:
                        apply_op()
                    ops.append(token)

            while ops:
                apply_op()

            return values[0] if values else "計算エラー"
        except:
            return "計算エラー"

    if not re.fullmatch(r'[0-9+\-*/().\s]+', expression):
        await ctx.reply("不正な文字が含まれています。")
        return

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(safe_calculate, expression), 
            timeout=0.1
        )
        await ctx.reply(content=result)

    except asyncio.TimeoutError:
        await ctx.reply("計算が重すぎます。")
    except Exception as e:
        await ctx.reply("計算エラー")


bot.run(os.environ.get('TOKEN'))