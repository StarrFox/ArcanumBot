# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="arcanumbot",
    version="1.1.0",
    packages=["arcanumbot", "arcanumbot.extensions"],
    url="https://github.com/StarrFox/ArcanumBot",
    license="GNU Affero General Public License",
    author="StarrFox",
    author_email="",
    description="A discord bot for the arcanum's archives discord",
    entry_points={"console_scripts": ["arcanumbot = arcanumbot.__main__:main"]},
    install_requires=[
        "aiosqlite",
        "discord.py @ git+https://github.com/Rapptz/discord.py@refs/pull/1849/merge",
        "jishaku",
        "humanize",
        "pendulum",
        "numpy",
        "python-box",
        "reusables",
    ],
)
