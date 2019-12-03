from discord.ext import commands

SCHOLAR_ID = 385972092010496000

def is_scholar_or_above():
    def pred(ctx: commands.Context):
        if not ctx.guild:
            return
        if ctx.author.top_role >= ctx.guild.get_role(SCHOLAR_ID):
            return True
        return False 
    return commands.check(pred)