from discord.ext import commands


def is_coin_mod_or_above():
    def pred(ctx: commands.Context):
        if not ctx.guild:
            return False

        coin_mod_role = ctx.guild.get_role(
            ctx.bot.config["general"].getint("coin_mod_role_id")
        )

        # Different guild
        if not coin_mod_role:
            return False

        if ctx.author.top_role >= coin_mod_role:
            return True

        return False

    return commands.check(pred)
