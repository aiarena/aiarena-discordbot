import discord, json, glob, os, requests, shutil, sys
from discord.ext import commands
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config

from cogs.exceptions import APIException
import cogs.request_generator as ai_arena_urls
import cogs.api as ai_arena_api

file_path = './replays/'  # insert file path

race_dict = {"P": "Protoss", "T": "Terran", "Z": "Zerg", "R": "Random"}


class Ladder(commands.Cog, name="urls"):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def send_files(context, directory: str):
        if len(glob.glob(directory + '/*.SC2Replay')) == 0:
            await context.message.author.send(f"Could not find any SC2 replays with the criteria: "
                                              f"{context.message.content}")
            return
        await context.message.author.send(f"Sending you {len(glob.glob(directory + '/*.SC2Replay'))} SC2 replay files...")
        for file in glob.glob(directory + "/*.SC2Replay"):
            try:
                await context.message.author.send(file=discord.File(file))
            except Exception as e:
                await context.message.author.send(f"Replay {file.split('/')[-1]} is too big!")
        await context.message.author.send(f"Have a nice day {config.SMILEY}")
        shutil.rmtree(directory)

    @commands.command(name="top10")
    async def top10(self, context):
        request_url = ai_arena_urls.make_top_ten_bots_request()
        response = requests.get(ai_arena_urls.make_top_ten_bots_request(), headers=config.AUTH)
        if response.status_code != 200:
            raise APIException("Could not retrieve top 10 bots!", request_url, response)
        bots = json.loads(response.text)

        bot_infos = []
        for participant in bots["results"]:
            b_id = participant["bot"]
            bot_info = ai_arena_api.get_bot_info(b_id)
            bot_infos.append((bot_info["name"], participant["elo"]))

        embed = discord.Embed(
            title="Leaderboard",
            description="Top 10 Bots",
            color=0x00FF00
        )

        for bot in bot_infos:
            embed.add_field(
                name=f"{bot[0]}",
                value=f"ELO: {bot[1]}",
                inline=False
            )
        await context.reply(embed=embed)

    @commands.command(name="top16")
    async def top16(self, context):
        request_url = ai_arena_urls.make_top_sixteen_bots_request()
        response = requests.get(request_url, headers=config.AUTH)
        if response.status_code != 200:
            raise APIException("Could not retrieve top 10 bots!", request_url, response)
        bots = json.loads(response.text)

        bot_infos = []
        for participant in bots["results"]:
            b_id = participant["bot"]
            bot_info = ai_arena_api.get_bot_info(b_id)
            bot_infos.append((bot_info["name"], participant["elo"]))

        embed = discord.Embed(
            title="Leaderboard",
            description="Top 16 Bots",
            color=0x00FF00
        )

        for bot in bot_infos:
            embed.add_field(
                name=f"{bot[0]}",
                value=f"ELO: {bot[1]}",
                inline=False
            )
        await context.reply(embed=embed)

    @commands.command(name="gg")
    async def gg(self, context):
        # if len(str(context.message.content).split(" ")) not in [3, 4, 6, 8]:
        #     raise Exception("Usage: !gg <bot_name> <num_days> optional --loss --tag <tag_name> --limit <num_replays>")
        args = str(context.message.content).split(" ")
        bot_name = args[1]
        bot_id = ai_arena_api.get_bot_id_by_name(bot_name)
        days = int(args[2])
        only_losses = "--loss" in str(context.message.content)
        tag = ""
        if "--tag" in str(context.message.content):
            for i, arg in enumerate(args):
                if arg == "--tag":
                    tag = args[i+1]

        limit = 999
        if "--limit" in str(context.message.content):
            for i, arg in enumerate(args):
                if arg == "--limit":
                    limit = int(args[i+1])
        replays = ai_arena_api.get_bot_matches(bot_name, bot_id, days, only_losses, tag, limit)
        await self.send_files(context, replays)

    @commands.command(name="bot")
    async def get_bot(self, context):
        if len(str(context.message.content).split(" ")) != 2:
            raise Exception("Usage: !bot <bot_name> ")

        bot_name = str(context.message.content).split(" ")[1]
        bot_id = ai_arena_api.get_bot_id_by_name(bot_name)
        bot_info = ai_arena_api.get_bot_info(bot_id)
        # Have to linearly traverse the competition participants in descending ELO order to get this bot's rank
        # The API could be improved to prevent having to do this.
        response = requests.get(config.LADDER_RANKS, headers=config.AUTH)
        if response.status_code != 200:
            raise APIException("Failed to look up bot elo and rank", config.LADDER_RANKS, response)
        ladder_info = json.loads(response.text)
        bot_info["rank"] = "unknown"
        bot_info["elo"] = "unknown"
        for i, info in enumerate(ladder_info["results"]):
            if info["bot"] == bot_id:
                bot_info["elo"] = info["elo"]
                bot_info["rank"] = i + 1
                break
        embed = discord.Embed(
            title=f"{bot_name}",
            description="Bot Information",
            color=0x00FF00
        )
        embed.add_field(
            name="Race",
            value=race_dict[bot_info["plays_race"]],
            inline=False
        )
        embed.add_field(
            name="Rank",
            value=bot_info["rank"],
            inline=False
        )
        embed.add_field(
            name="ELO",
            value=bot_info["elo"],
            inline=False
        )
        embed.add_field(
            name="Last Updated",
            value=bot_info["bot_zip_updated"].split("T")[0],
            inline=False
        )
        embed.add_field(
            name="Downloadable?",
            value=bot_info["bot_zip_publicly_downloadable"],
            inline=False
        )
        await context.reply(embed=embed)


def setup(bot):
    bot.add_cog(Ladder(bot))