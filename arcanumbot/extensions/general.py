from discord.ext import commands


class General(commands.Cog, name="general"):
    @commands.command()
    async def ping(self, ctx: commands.Context):
        """
        Sends the bot's websocket latency
        """
        await ctx.send(
            f"\N{TABLE TENNIS PADDLE AND BALL} {round(ctx.bot.latency * 1000)}ms"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
