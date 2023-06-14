import logging
import os
from pathlib import Path

import click

from arcanumbot import ArcanumBot

# only works on linux
try:
    import uvloop
except ImportError:
    uvloop = None
else:
    uvloop.install()


os.environ["JISHAKU_HIDE"] = "true"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "true"
os.environ["JISHAKU_NO_UNDERSCORE"] = "true"
os.environ["JISHAKU_RETAIN"] = "true"


@click.command()
@click.option(
    "--secret",
    help="Path to secret file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default="discord_token.secret",
)
def main(secret: Path):
    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)s:%(name)s] %(message)s", level=logging.INFO
    )

    logging.getLogger("discord").setLevel(logging.ERROR)

    bot = ArcanumBot()

    with open(secret) as fp:
        discord_token = fp.read().strip("\n")

    bot.run(discord_token)


if __name__ == "__main__":
    main()
