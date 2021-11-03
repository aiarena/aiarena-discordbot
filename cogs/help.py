import os, sys, discord
from discord.ext import commands
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config


class Help(commands.Cog, name="help"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, context):
        # Note that commands made only for the owner of the bot are not listed here.
        embed = discord.Embed(
            title="Bot",
            description="List of commands are:",
            color=0x00FF00
        )
        embed.add_field(
            name="!invite",
            value="Get a discord invite link.",
            inline=False
        )
        embed.add_field(
            name="!top10",
            value="Top 10 ranked bots.",
            inline=False
        )
        embed.add_field(
            name="!top16",
            value="Top 16 ranked bots.",
            inline=False
        )
        embed.add_field(
            name="!bot <bot name>",
            value="Shows Bot information.",
            inline=False
        )
        embed.add_field(
            name="!gs || !gettingstarted",
            value="Shows getting started infos.",
            inline=False
        )
        embed.add_field(
            name="!gg <bot_name> <num_replays> optional: --loss",
            value="Creates and uploads a replay pack of <bot_name>'s last <num_replays> games. If \"--loss\" is"
                  "specified, the replays will be only of games where the bot lossed.",
            inline=False
        )
        embed.add_field(
            name="!tag <tag_name> <num_days>",
            value="Creates and uploads a replay pack of matches with the tag <tag_name> from the last <num_days>",
            inline=False
        )
        await context.reply(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
