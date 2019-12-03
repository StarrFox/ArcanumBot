import json
import config
import discord
import logging

from extras import checks
from discord.ext import commands
from bot_stuff import DiscordHandler

logger = logging.getLogger(__name__)
logger.propagate = False

logger.addHandler(
    DiscordHandler(
        config.webhook_url,
        logging.INFO
    )
)

class aacoins(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.coins = {} # id: ammount
        self.load_coins()

    def load_coins(self):
        with open('aacoins.json', 'a+') as fp:
            fp.seek(0)
            if len(fp.read()) == 0:
                self.coins = {}
            else:
                fp.seek(0)
                temp = json.load(fp)
                # convert keys to ints
                self.coins = {k: i for k, i in map(lambda ki: (int(ki[0]), ki[1]), temp.items())}
        self.save_coins()
        logger.info(f"Loaded aacoins for {len(self.coins.keys())} users.")

    def save_coins(self):
        with open('aacoins.json', 'w+') as fp:
            json.dump(self.coins, fp, indent=4)
        logger.info(f"Saved aacoins for {len(self.coins.keys())} users.")

    def cog_unload(self):
        self.save_coins()

    @commands.command(name='coins')
    async def view_aacoins(self, ctx: commands.Context, member: discord.Member = None):
        """
        view your or another member's aacoin amount
        """
        member = member or ctx.author
        amount = self.coins.get(member.id) or 0
        await ctx.send(f"{member} has {amount} aacoin(s)")

    @commands.command(name='add')
    @checks.is_scholar_or_above()
    async def add_aacoins(self, ctx: commands.Context, member: discord.Member, amount: int):
        """
        Add aacoins to a member
        """
        self.coins[member.id] = (self.coins.get(member.id) or 0) + amount
        self.save_coins()
        await ctx.send(f"Added {amount} to {member}'s aacoin(s)")

    @commands.command(name='remove')
    @checks.is_scholar_or_above()
    async def remove_aacoins(self, ctx: commands.Context, member: discord.Member, amount: int):
        """
        Remove aacoins from a member
        """
        self.coins[member.id] = (self.coins.get(member.id) or 0) - amount
        self.save_coins()
        await ctx.send(f"Remove {amount} from {member}'s aacoin(s)")

    @commands.command(name="sendfile")
    @checks.is_scholar_or_above()
    async def send_aacoins_file(self, ctx: commands.Context):
        """
        Sends aacoins file
        """
        await ctx.send(file=discord.File("aacoins.json"))

def setup(bot: commands.Bot):
    bot.add_cog(aacoins(bot))