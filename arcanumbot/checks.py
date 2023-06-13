import discord
from discord.ext import commands

from . import constants


def is_coin_mod_or_above():
    def pred(ctx: commands.Context):
        if ctx.guild is None:
            return False

        coin_mod_role = ctx.guild.get_role(constants.coin_mod_role_id)

        # Different guild
        if coin_mod_role is None:
            return False

        if isinstance(ctx.author, discord.User):
            return False

        if ctx.author.top_role >= coin_mod_role:
            return True

        return False

    return commands.check(pred)
