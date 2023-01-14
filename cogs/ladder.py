import argparse, discord, json, glob, requests, shutil
from discord.ext import commands
import config

from cogs.exceptions import APIException
import cogs.request_generator as ai_arena_urls
import cogs.api as ai_arena_api

file_path = './replays/'  # insert file path

race_dict = {"P": "Protoss", "T": "Terran", "Z": "Zerg", "R": "Random"}


class Ladder(commands.Cog, name="ladder"):
    def __init__(self, bot):
        self.bot = bot

    # Unused, can be removed?
    # @staticmethod
    # async def get_discord_name(self, context: discord.ext.commands.Context, discord_id: str):
    #     discord_user = await context.message.guild.get_member(discord_id)
    #     return discord_user.nick

    @staticmethod
    async def send_files(context: discord.ext.commands.Context, directory: str):
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
    async def top10(self, context: discord.ext.commands.Context):
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
    async def top16(self, context: discord.ext.commands.Context):
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
    async def gg(self, context: discord.ext.commands.Context):
        parser = argparse.ArgumentParser(prog='gg')
        parser.add_argument('bot_name', type=str, help='bot name')
        parser.add_argument('days', type=int, default=3, help='number of days')
        parser.add_argument('--limit', required=False, type=int, default=5, help='max number of replays to query')
        parser.add_argument('--losses', required=False, default=False, action='store_true')
        parser.add_argument('--tag', required=False, type=str, default="", help='tag to look for')

        args, unknown = parser.parse_known_args(context.message.content.split()[1:])
        print(args, unknown)
        if unknown:
            await context.reply("!gg <bot_name> <num_days>  optional arguments: "
                                "--limit <max_replays> --losses --tag <tag_name>")
            return

        bot_id = ai_arena_api.get_bot_id_by_name(args.bot_name)
        replays = ai_arena_api.get_bot_matches(args.bot_name, bot_id, args.days, args.losses, args.tag, args.limit)
        await self.send_files(context, replays)

    @commands.command(name="bot")
    async def get_bot(self, context: discord.ext.commands.Context):
        if len(context.message.content.split(" ")) != 2:
            raise Exception("Usage: !bot <bot_name> ")

        bot_name = context.message.content.split(" ")[1]
        bot_id = ai_arena_api.get_bot_id_by_name(bot_name)
        bot_info = ai_arena_api.get_bot_info(bot_id)
        elo_change = ai_arena_api.get_elo_change(bot_name, bot_id, bot_info["bot_zip_updated"])

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

        author_name = bot_info["author_info"][0] + " - AI Arena"
        # author on discord, get discord name
        if bot_info["author_info"][1]:
            author_name = await self.bot.fetch_user(bot_info["author_info"][0])
            author_name = author_name.name + " - Discord"

        embed = discord.Embed(
            title="Bot Information",
            description=f"{bot_name}",
            color=0x00FF00
        )
        embed.add_field(
            name="Author",
            value=author_name,
            inline=False
        )
        embed.add_field(
            name="Race",
            value=race_dict[bot_info["plays_race"]['label']],
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
            name="ELO Change since last update",
            value=elo_change,
            inline=False
        )
        embed.add_field(
            name="Last Updated",
            value=bot_info["bot_zip_updated"].split("T")[0],
            inline=False
        )
        embed.add_field(
            name="Downloadable",
            value=bot_info["bot_zip_publicly_downloadable"],
            inline=False
        )
        await context.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Ladder(bot))