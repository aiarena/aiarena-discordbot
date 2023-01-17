from discord.ext import commands
import discord


class URLS(commands.Cog, name="urls"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="invite")
    async def invite(self, context: discord.ext.commands.Context):
        await context.reply("https://discordapp.com/invite/Emm5Ztz")

    @commands.command(name="stream")
    async def stream(self, context: discord.ext.commands.Context):
        await context.reply("Stream URL: <https://www.twitch.tv/aiarenastream>")

    @commands.command(name="maps")
    async def maps(self, context: discord.ext.commands.Context):
        await context.reply("Maps for the season: <https://aiarena.net/wiki/maps/>")

    @commands.command(name="gettingstarted", aliases=["gs"])
    async def getting_started(self, context: discord.ext.commands.Context):
        await context.reply("Getting started: https://aiarena.net/wiki/bot-development/getting-started/")

    @commands.command(name="trello")
    async def trello(self, context: discord.ext.commands.Context):
        await context.reply("""Trello boards:
General/misc: <https://trello.com/b/ykMT2vyR/ai-arena-general>
Website: <https://trello.com/b/qw4DYU9H/ai-arena-website>
Arena Client: <https://trello.com/b/a7cUfzl0/ai-arena-client>
Devop: <https://trello.com/b/Tu2GR6gn/ai-arena-devop>""")

async def setup(bot):
    await bot.add_cog(URLS(bot))