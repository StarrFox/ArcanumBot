import logging
from datetime import timedelta

from discord.ext import commands
from humanize import naturaldelta

logger = logging.getLogger(__name__)


async def on_command_error(ctx: commands.Context, error):
    error = getattr(error, "original", error)

    if isinstance(error, commands.CommandNotFound):
        return

    # Bypass checks for owner
    elif isinstance(error, commands.CheckFailure) and await ctx.bot.is_owner(
        ctx.author
    ):
        await ctx.reinvoke()
        return

    # Reset cooldown when command doesn't finish
    elif isinstance(error, commands.CommandError) and not isinstance(
        error, commands.CommandOnCooldown
    ):
        if ctx.command is not None:
            ctx.command.reset_cooldown(ctx)

        return await ctx.send(str(error))

    elif isinstance(error, commands.CommandOnCooldown):
        delta = timedelta(seconds=error.retry_after)
        natural = naturaldelta(delta)
        return await ctx.send(f"Command on cooldown, retry in {natural}.")

    if ctx.command is not None:
        logger.error(
            f"Unhandled error in command {ctx.command.name}\nInvoke message: {ctx.message.content}\n{error=}"
        )

    await ctx.send(f"Unknown error while executing {ctx.command}, will be fixed soon.")


async def setup(bot: commands.Bot):
    bot.add_listener(on_command_error)


async def teardown(bot: commands.Bot):
    bot.remove_listener(on_command_error)
