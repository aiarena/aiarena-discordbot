import os, sys, discord
from discord.ext import commands
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config

class Ladder(commands.Cog, name="urls"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="!top10")
    async def invite(self, context):
        await context.send("Not Implemented!")

    @commands.command(name="!top16")
    async def stream(self, context):
        await context.send("Not Implemented!")

def setup(bot):
    bot.add_cog(Ladder(bot))