import asyncio
import re

from discord.ext import commands, tasks
import discord
from tags import Parser

class MathCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()

        self.bot = bot

    @commands.hybrid_command(name="calc", description="計算をします。", aliases=["math"])
    @commands.cooldown(2, 5, type=commands.BucketType.user)
    async def help(self, ctx: commands.Context, expression: str):
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

async def setup(bot):
    await bot.add_cog(MathCog(bot))