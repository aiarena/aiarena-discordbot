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
            value="Shouws Bot information.",
            inline=False)
        embed.add_field(
            name="!trello",
            value="Shows Trello board links.",
            inline=False
        )
        embed.add_field(
            name="!gs || !gettingstarted",
            value="Shows getting started infos.",
            inline=False
        )
        embed.add_field(
            name="!gg <bot_name> <num_days>  optional arguments: --loss --tag <tag_name>",
            value="Creates and uploads a replay pack of <bot_name>'s last <num_days> games. If \"--loss\" is"
                  "specified, the replays will be only of games where the bot lossed."
                  "If \"--tag <tag_name>\" is specified, only replays tagged with <tag_name> will be included"
                  "If \"--limit <num_replays>\" is specified, only <num_replays> will be sent"
                  "Note: Only the previous 250 matches of any bot will be looked at",
            inline=False
        )
        await context.reply(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
