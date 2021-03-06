import os, sys, discord
from discord.ext import commands
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config

class URLS(commands.Cog, name="urls"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="!invite")
    async def invite(self, context):
        await context.send("https://discordapp.com/invite/Emm5Ztz")

    @commands.command(name="stream")
    async def stream(self, context):
        await context.send("Stream URL: <https://www.twitch.tv/aiarenastream>")

    @commands.command(name="gs")
    async def gs(self, context):
        await context.send("Getting started: https://aiarena.net/wiki/bot-development/getting-started/")

    @commands.command(name="gettingstarted")
    async def getting_started(self, context):
        await context.send("Getting started: https://aiarena.net/wiki/bot-development/getting-started/")

    @commands.command(name="!stream")
    async def stream(self, context):
        await context.send("Time until the next stream: https://www.timeanddate.com/worldclock/fixedtime.html?msg=stream&iso=20201027T21&p1=101&ah=1&am=30")

def setup(bot):
    bot.add_cog(URLS(bot))