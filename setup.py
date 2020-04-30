# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='arcanumbot',
    version='1.0.1',
    packages=['arcanumbot'],
    url='https://github.com/StarrFox/ArcanumBot',
    license='GNU Affero General Public License',
    author='StarrFox',
    author_email='',
    description='A discord bot for the arcanum\'s archives discord',
    install_requires=[
        'aiosqlite',
        'discord.py @ git+https://github.com/Rapptz/discord.py@refs/pull/1849/merge',
        'jishaku',
        'humanize',
        'discord-chan @ git+https://github.com/StarrFox/Discord-chan',
        'pendulum'
    ]
)
