import logging
from random import choice

import discord
from discord.ext import commands

from arcanumbot import (
    ArcanumBot,
    ConfirmationMenu,
    Connect4,
    EmojiGameMenu,
    MasterMindMenu,
    MenuPages,
    NormalPageSource,
    SubContext,
    checks,
    db,
)

logger = logging.getLogger(__name__)

CONNECT4_WIN = 100
CONNECT4_LOSE = 25
CONNECT4_TIE = 65


class IsOnCooldown(commands.CommandError):
    pass


def is_on_cooldown(command_name):
    async def predicate(ctx):
        if await ctx.bot.is_on_cooldown(command_name, ctx.author.id):
            raise IsOnCooldown(
                f"Sorry {ctx.author.display_name}, you can play {command_name} again at midnight CT."
            )

        else:
            return True

    return commands.check(predicate)


class aacoins(commands.Cog):
    def __init__(self, bot: ArcanumBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild != self.bot.guild:
            return

        logger.info(f"{member} left guild.")
        coins = await self.bot.get_aacoin_amount(member.id)

        if coins:
            await self.bot.prompt_delete(member.id)

    @commands.group(name="coins", invoke_without_command=True)
    async def view_aacoins(self, ctx: commands.Context, member: discord.Member = None):
        """
        View another member or your aacoin amount.
        """
        member = member or ctx.author
        amount = await self.bot.get_aacoin_amount(member.id)
        plural = amount != 1
        await ctx.send(
            f"{member} has {amount} {ctx.bot.aacoin}{'s' if plural else ''}."
        )

    @view_aacoins.command(name="all")
    async def view_all_aacoins(self, ctx: commands.Context):
        """
        View all aacoins sorted by amount.
        """
        lb = await self.bot.get_aacoin_lb()

        entries = []
        for user_id, coins in lb:
            # attempt cache pull first
            if (member := ctx.guild.get_member(user_id)) is None:
                member = await self.bot.guild.fetch_member(user_id)

            entries.append(f"{member}: {coins}")

        source = NormalPageSource(entries, per_page=10)

        menu = MenuPages(source)

        await menu.start(ctx)

    @commands.command(name="add")
    @checks.is_coin_mod_or_above()
    async def add_aacoins(
        self, ctx: commands.Context, member: discord.Member, amount: int
    ):
        """
        Add aacoins to a member.
        """
        current = await self.bot.get_aacoin_amount(member.id)
        await self.bot.set_aacoins(member.id, current + amount)
        message = f"Added {amount} to {member}'s {ctx.bot.aacoin} balance."
        await ctx.send(message)

    @commands.command(name="remove", aliases=["rem"])
    @checks.is_coin_mod_or_above()
    async def remove_aacoins(
        self, ctx: commands.Context, member: discord.Member, amount: int
    ):
        """
        Remove aacoins from a member.
        """
        current = await self.bot.get_aacoin_amount(member.id)
        await self.bot.set_aacoins(member.id, current - amount)
        message = f"Removed {amount} from {member}'s {ctx.bot.aacoin} balance."
        await ctx.send(message)

    @commands.command(name="clear_command")
    @checks.is_coin_mod_or_above()
    async def clear_aacoins(self, ctx: commands.Context, member: discord.Member):
        """
        Clear a member's aacoin(s).
        """
        await self.bot.delete_user_aacoins(member.id)
        message = f"Cleared {member}'s {ctx.bot.aacoin} balance"
        await ctx.send(message)

    @commands.command(name="cooldown-reset", aliases=["cr"])
    @checks.is_coin_mod_or_above()
    async def cooldown_reset(
        self, ctx: SubContext, identifier: str, member: discord.Member
    ):
        async with db.get_database() as conn:
            await conn.execute(
                "DELETE FROM cooldowns WHERE command_name = (?) AND user_id = (?);",
                (identifier, member.id),
            )

            await conn.commit()

        await ctx.send("reset.")

    @commands.command(name="react")
    @commands.max_concurrency(1, commands.BucketType.user)
    @is_on_cooldown("React")
    async def aacoins_react_game(self, ctx: SubContext):
        """
        Play a game of Emoji react; can only be played once a day.
        """
        game = EmojiGameMenu()
        value = await game.run(ctx)

        if value:
            current = await self.bot.get_aacoin_amount(ctx.author.id)
            await self.bot.set_aacoins(ctx.author.id, current + value)

            await ctx.send(
                f"\N{PARTY POPPER} {ctx.author.mention} won {value} {ctx.bot.aacoin}s\n"
                f"they now have a total of {await self.bot.get_aacoin_amount(ctx.author.id)}"
            )

        else:
            await ctx.send(f"{ctx.author.mention}, React timed out.")

    @aacoins_react_game.after_invoke
    async def after_aacoins_react_game(self, ctx: commands.Context):
        await ctx.bot.set_cooldown("React", ctx.author.id)

    @commands.command(name="mastermind")
    @commands.max_concurrency(1, commands.BucketType.user)
    @is_on_cooldown("MasterMind")
    async def aacoins_mastermind_game(self, ctx: SubContext):
        """
        Play a game of mastermind; can only be played once a day.
        Time outs count as games played.
        """
        game = MasterMindMenu()
        value = await game.run(ctx)

        if value:
            current = await self.bot.get_aacoin_amount(ctx.author.id)
            await self.bot.set_aacoins(ctx.author.id, current + value)

            await ctx.send(
                f"\N{PARTY POPPER} {ctx.author.mention} won {value} {ctx.bot.aacoin}s\n"
                f"they now have a total of {await self.bot.get_aacoin_amount(ctx.author.id)}"
            )

        elif value == 0:
            return

        else:
            await ctx.send(f"{ctx.author.mention}, MasterMind timed out.")

    @aacoins_mastermind_game.after_invoke
    async def after_aacoins_mastermind_game(self, ctx: commands.Context):
        await ctx.bot.set_cooldown("MasterMind", ctx.author.id)

    @commands.command(name="connect4", aliases=["c4"])
    @commands.max_concurrency(1, commands.BucketType.channel)
    @is_on_cooldown("Connect4")
    async def aacoins_connect4_game(self, ctx: SubContext, member: discord.Member):
        """
        Play a game of connect4 with another member; the command user will be put on cooldown.
        """
        if member == ctx.author or member.bot:
            return await ctx.send("You cannot play against yourself or a bot.")

        menu = ConfirmationMenu(f"{member.mention} agree to play?", owner_id=member.id)
        if not await menu.get_response(ctx):
            return await ctx.send("Game canceled.")

        player1 = choice([ctx.author, member])
        player2 = member if player1 == ctx.author else ctx.author

        game = Connect4(player1, player2)
        winner = await game.run(ctx)
        if winner:
            if isinstance(winner, tuple):
                # Todo: make a convince method for this
                current = await self.bot.get_aacoin_amount(winner[0].id)
                await self.bot.set_aacoins(winner[0].id, current + CONNECT4_TIE)
                current = await self.bot.get_aacoin_amount(winner[1].id)
                await self.bot.set_aacoins(winner[1].id, current + CONNECT4_TIE)
                await ctx.send(
                    f"{player1.mention} and {player2.mention} tied and both gained {CONNECT4_TIE}{ctx.bot.aacoin}s."
                )
            else:
                loser = player1 if winner == player2 else player2
                current = await self.bot.get_aacoin_amount(winner.id)
                await self.bot.set_aacoins(winner.id, current + CONNECT4_WIN)
                current = await self.bot.get_aacoin_amount(loser.id)
                await self.bot.set_aacoins(loser.id, current + CONNECT4_LOSE)
                await ctx.send(
                    f"{winner.mention} has won and gained {CONNECT4_WIN}{ctx.bot.aacoin}s.\n"
                    f"{loser.mention} gained {CONNECT4_LOSE}{ctx.bot.aacoin}s for playing."
                )
            # Todo: Fix
            await ctx.bot.set_cooldown("Connect4", ctx.author.id)
        else:
            await ctx.send("No one made a move.")

    # @commands.command(name="typeracer")
    # async def aacoins_typeracer(self, ctx: SubContext):
    #     """help string"""
    #     game = TypeRacer(self.bot, ctx)
    #     await ctx.send(await game.run())


async def setup(bot: ArcanumBot):
    await bot.add_cog(aacoins(bot))
