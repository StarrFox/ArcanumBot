import json
import config
import discord
import logging

from extras import checks
from discord.ext import commands
from collections import defaultdict
from bot_stuff import DiscordHandler
from jishaku.paginators import WrappedPaginator, PaginatorEmbedInterface

logger = logging.getLogger(__name__)
logger.propagate = False

if not logger.handlers:
    logger.addHandler(
        DiscordHandler(
            config.webhook_url,
            logging.INFO
        )
    )

class aacoins(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.coins = defaultdict(lambda: 0) # returns 0 if key not in dict
        if config.load_aacoins:
            self.load_coins()

    def remove_zeros(self):
        to_remove = []
        for key, value in self.coins.items():
            if value == 0:
                to_remove.append(key)
        for key in to_remove:
            del self.coins[key]
        if to_remove:
            logger.info(f"Removed ({', '.join(map(str, to_remove))}) from aacoins for having 0.")

    def load_coins(self):
        with open('aacoins.json', 'a+') as fp:
            fp.seek(0)
            if len(fp.read()) == 0:
                return
            else:
                fp.seek(0)
                temp = json.load(fp)
                # convert keys to ints
                self.coins.update({int(k): i for k, i in temp.items()})
        self.save_coins()
        logger.info(f"Loaded aacoins for {len(self.coins.keys())} users.")

    def save_coins(self):
        if not config.load_aacoins:
            return
        self.remove_zeros()
        if len(self.coins) == 0:
            return
        with open('aacoins.json', 'w+') as fp:
            json.dump(self.coins, fp, indent=4)
        logger.info(f"Saved aacoins for {len(self.coins.keys())} users.")

    def cog_unload(self):
        self.save_coins()

    @commands.group(name='coins', invoke_without_command=True)
    async def view_aacoins(self, ctx: commands.Context, member: discord.Member = None):
        """
        View your or another member's aacoin amount
        """
        member = member or ctx.author
        amount = self.coins[member.id]
        await ctx.send(f"{member} has {amount} aacoin(s)")

    @view_aacoins.command(name='all')
    async def view_all_aacoins(self, ctx: commands.Context):
        """
        View all aacoins sorted by amount
        """
        message = '\n'.join(
            [f"{self.bot.get_user(k)}: {v}" for k, v in reversed(sorted(self.coins.items(), key=lambda kv: kv[1]))]
        )

        paginator = WrappedPaginator(prefix='', suffix='') # TODO: use None here after it's supported

        paginator.add_line(message)

        interface = PaginatorEmbedInterface(self.bot, paginator, owner=ctx.author)

        await interface.send_to(ctx)

    @commands.command(name='add')
    @checks.is_scholar_or_above()
    async def add_aacoins(self, ctx: commands.Context, member: discord.Member, amount: int):
        """
        Add aacoins to a member
        """
        self.coins[member.id] += amount
        self.save_coins()
        message = f"Added {amount} to {member}'s aacoin(s)"
        await ctx.send(message)
        logger.info(message)

    @commands.command(name='remove')
    @checks.is_scholar_or_above()
    async def remove_aacoins(self, ctx: commands.Context, member: discord.Member, amount: int):
        """
        Remove aacoins from a member
        """
        self.coins[member.id] -= amount
        self.save_coins()
        message = f"Removed {amount} from {member}'s aacoin(s)"
        await ctx.send(message)
        logger.info(message)

    @commands.command(name='clear')
    @checks.is_scholar_or_above()
    async def clear_aacoins(self, ctx: commands.Context, member: discord.Member):
        """
        Clear a member's aacoin(s)
        """
        self.coins[member.id] = 0
        self.save_coins()
        message = f"Cleared {member}'s aacoin(s)"
        await ctx.send(message)
        logger.info(message)

    @commands.command(name="sendfile")
    @checks.is_scholar_or_above()
    async def send_aacoins_file(self, ctx: commands.Context):
        """
        Sends aacoins file
        """
        await ctx.send(file=discord.File("aacoins.json"))

def setup(bot: commands.Bot):
    bot.add_cog(aacoins(bot))