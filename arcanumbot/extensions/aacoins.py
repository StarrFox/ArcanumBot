import logging
from random import choice
from typing import Optional

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

        coins = await self.bot.get_aacoin_amount(member.id)

        if coins:
            logger.info(f"Dropping {member}({member.id}) from coins db; they had {coins} coins")

            await self.bot.delete_user_aacoins(member.id)

            await self.bot.logging_channel.send(
                f"Dropped {member}({member.id}) from coins db; they had {coins} coins"
            )

    @commands.group(name="coins", invoke_without_command=True)
    async def view_aacoins(
        self, ctx: commands.Context, member: Optional[discord.Member] = None
    ):
        """
        View another member or your aacoin amount.
        """
        if member is None:
            # global command check prevents commands from being used in dms
            assert isinstance(ctx.author, discord.Member)
            member = ctx.author

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
            assert ctx.guild is not None
            # attempt cache pull first
            if (member := ctx.guild.get_member(user_id)) is not None:
                entries.append(f"{member}: {coins}")
                continue

            try:
                member = str(await self.bot.guild.fetch_member(user_id))
            except discord.NotFound:
                logger.warning(f"Unbound user id {user_id} in coin db")
                member = str(user_id)
            except Exception as exc:
                logger.critical(f"Unhandled exception in view all: {exc}")
                member = str(user_id)
            finally:
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
        await self.bot.add_aacoins(member.id, amount)
        await ctx.send(f"Added {amount} to {member}'s {ctx.bot.aacoin} balance.")

    @commands.command(name="remove", aliases=["rem"])
    @checks.is_coin_mod_or_above()
    async def remove_aacoins(
        self, ctx: commands.Context, member: discord.Member, amount: int
    ):
        """
        Remove aacoins from a member.
        """
        await self.bot.remove_aacoins(member.id, amount)
        await ctx.send(f"Removed {amount} from {member}'s {ctx.bot.aacoin} balance.")

    @commands.command(name="clear")
    @checks.is_coin_mod_or_above()
    async def clear_aacoins(self, ctx: commands.Context, member: discord.Member):
        """
        Clear a member's aacoin(s).
        """
        ammount = await self.bot.get_aacoin_amount(member.id)
        await self.bot.delete_user_aacoins(member.id)
        await ctx.send(f"Cleared {member}'s {ctx.bot.aacoin} balance of {ammount}")

    @commands.command(name="cooldown-reset", aliases=["cr"])
    @checks.is_coin_mod_or_above()
    async def cooldown_reset(
        self, ctx: SubContext, member: discord.Member
    ):
        await self.bot.clear_cooldowns_for_user(member.id)
        await ctx.send(f"Reset cooldowns for {member}")

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

        assert isinstance(player1, discord.Member)
        assert isinstance(player2, discord.Member)

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
            # TODO: figure out what needed to be fixed
            # Todo: Fix
            await ctx.bot.set_cooldown("Connect4", ctx.author.id)
        else:
            await ctx.send("No one made a move.")


async def setup(bot: ArcanumBot):
    await bot.add_cog(aacoins(bot))
