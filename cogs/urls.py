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
        await context.reply("https://discordapp.com/invite/Emm5Ztz")

    @commands.command(name="stream")
    async def stream(self, context):
        await context.reply("Stream URL: <https://www.twitch.tv/aiarenastream>")

    @commands.command(name="gs")
    async def gs(self, context):
        await context.reply("Getting started: https://aiarena.net/wiki/bot-development/getting-started/")

    @commands.command(name="gettingstarted")
    async def getting_started(self, context):
        await context.reply("Getting started: https://aiarena.net/wiki/bot-development/getting-started/")

    @commands.command(name="next")
    async def next_stream(self, context):
        await context.reply("https://everytimezone.com/s/36096de8")

    @commands.command(name="!stream")
    async def stream(self, context):
<<<<<<< HEAD
        await context.send("Time until the next stream: https://www.timeanddate.com/worldclock/fixedtime.html?msg=stream&iso=20201027T21&p1=101&ah=1&am=30")
=======
        await context.reply("Trello boards:\n"+
                            "General/misc: https://trello.com/b/ykMT2vyR/ai-arena-general\n"+
                            "Website: https://trello.com/b/qw4DYU9H/ai-arena-website\n"+
                            "Arena Client: https://trello.com/b/a7cUfzl0/ai-arena-client\n"+
                            "Devop: https://trello.com/b/Tu2GR6gn/ai-arena-devop")
>>>>>>> d2d5081 (next, top16, tags commands)

def setup(bot):
    bot.add_cog(URLS(bot))