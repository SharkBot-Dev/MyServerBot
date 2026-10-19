from discord.ext import commands, tasks
import discord
from tags import Parser

class OwnerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()

        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, cog_name: str):
        await self.bot.reload_extension("cogs." + cog_name)
        await ctx.reply("✅")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx: commands.Context, cog_name: str):
        await self.bot.load_extension("cogs." + cog_name)
        await ctx.reply("✅")

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context):
        msg = await ctx.reply("<a:loading:1480529495114121279>")
        await self.bot.tree.sync()
        await msg.edit(content="✅")
        
    @commands.command()
    @commands.is_owner()
    async def echo(self, ctx: commands.Context, text: str):
        await ctx.channel.send(text)
        await ctx.message.delete()
        
    @commands.command()
    @commands.is_owner()
    async def embed(self, ctx: commands.Context, *, text: str):
        await ctx.channel.send(embed=discord.Embed(description=text))
        await ctx.message.delete()

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx: commands.Context, *, text: str):
        parser = Parser({
            "bot_id": str(self.bot.user.id),
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

        embeds = []

        async def addembed(globals, args):
            if not args:
                return ""

            try:
                _dict = {}
                for _ in " ".join(args).split(","):
                    data = _.split("=", 1)
                    if data[0] == "color":
                        _dict[data[0]] = int(data[1])
                        continue
                    if data[0] == "image":
                        _dict[data[0]] = {"url": data[1]}
                        continue
                    if data[0] == "thumbnail":
                        _dict[data[0]] = {"url": data[1]}
                        continue
                    if data[0] == "author":
                        if not _dict.get("author"):
                            _dict["author"] = {}
                        _dict["author"]["name"] = data[1]
                        continue
                    if data[0] == "author_icon":
                        if not _dict.get("author"):
                            _dict["author"] = {}
                        _dict["author"]["icon_url"] = data[1]
                        continue
                    if data[0] == "footer":
                        if not _dict.get("footer"):
                            _dict["footer"] = {}
                        _dict["footer"]["text"] = data[1]
                        continue
                    if data[0] == "footer_icon":
                        if not _dict.get("footer"):
                            _dict["footer"] = {}
                        _dict["footer"]["icon_url"] = data[1]
                        continue
                    _dict[data[0]] = data[1]

                embeds.append(discord.Embed.from_dict(_dict))
                return ""
            except:
                return ""

        parser.add_func("embed", addembed)
        parser.add_func("addembed", addembed)

        await ctx.channel.send(await parser.parse(text), embeds=embeds)
        await ctx.message.add_reaction("✅")

async def setup(bot):
    await bot.add_cog(OwnerCog(bot))