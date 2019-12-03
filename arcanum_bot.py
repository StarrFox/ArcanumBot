import config
import bot_stuff

from discord.ext import commands

jsk_settings = {
    "scope_prefix": "",
    "retain": True,
    "channel_tracebacks": True
}

bot = bot_stuff.Bot(config.prefix, extension_dir='cogs')

bot.help_command = bot_stuff.Minimal()

bot.load_extension("bot_stuff.jsk", **jsk_settings)

bot.load_extension("bot_stuff.logging_cog", webhook_url=config.webhook_url)

bot.run(config.token)