from discord.ext import commands

# Todo: fix role name
SCHOLAR_ID = 561659914267656202

def is_scholar_or_above():
    def pred(ctx: commands.Context):
        if not ctx.guild:
            return
        if ctx.author.top_role >= ctx.guild.get_role(SCHOLAR_ID):
            return True
        return False 
    return commands.check(pred)
