import discord, os, random, shutil, string, sys
from discord.ext import commands
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config

from cogs.exceptions import APIException

import json
import os

import requests

file_path = './replays/'  # insert file path
auth = {'Authorization': f'Token {config.API_TOKEN}'}

def get_bot_id_by_name(bot_name: str):
    response = requests.get(f'https://aiarena.net/api/bots/?name={bot_name}', headers=auth)
    if response.status_code != 200:
        return -1
    bot = json.loads(response.text)
    return bot["results"][0]["id"]

def get_bot_replays(bot_id: str, only_losses: bool) -> str:
    letters = string.ascii_lowercase
    file_path = ''.join(random.choice(letters) for i in range(10))
    os.mkdir(file_path)
    max_match = 999999
    num_replays = 0

    while num_replays < 3:
        if only_losses:
            response = requests.get(f'https://aiarena.net/api/match-participations/?result=loss&bot={bot_id}&max_match={max_match}&ordering=-match&limit=1', headers=auth)
        else:
            response = requests.get(f'https://aiarena.net/api/match-participations/?bot={bot_id}&max_match={max_match}&ordering=-match&limit=1', headers=auth)
        if response.status_code != 200:
            return ""
        participation = json.loads(response.text)
        print(f'Downloading match {participation["results"][0]["match"]}')
        response = requests.get(f'https://aiarena.net/api/results/?match={participation["results"][0]["match"]}', headers=auth)
        if response.status_code != 200:
            return ""
        max_match = int(participation['results'][0]["match"]) - 1
        match_details = json.loads(response.text)
        if len(match_details["results"]) == 0:
            continue
        replay_file = match_details['results'][0]['replay_file']
        if replay_file not in (None, 'null'):
            replay = requests.get(replay_file, headers=auth)
            with open(os.path.join(file_path, str(match_details["results"][0]["match"])+'.SC2Replay'), 'wb') as f:
                f.write(replay.content)
            num_replays += 1
    
    archive_name = str(bot_id) + str(file_path[0:2])
    shutil.make_archive(archive_name, 'zip', root_dir=file_path + '/')
    shutil.rmtree(os.path.join(os.getcwd(), file_path), ignore_errors=True)

    return archive_name

def clean_up_archive(archive_name: str):
    os.remove(archive_name + ".zip")

class Ladder(commands.Cog, name="urls"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="top10")
    async def top10(self, context):
        response1 = requests.get(
            "https://aiarena.net/api/competition-participations/?competition=3&ordering=-elo&limit=10", headers=auth)
        if response1.status_code != 200:
            print("get error 1")
        bots = json.loads(response1.text)

        bot_infos = []
        for participant in bots["results"]:
            b_id = participant["bot"]
            response2 = requests.get(
                f"https://aiarena.net/api/bots/{b_id}/", headers=auth)
            if response2.status_code != 200:
                print("get error 2")
            info = json.loads(response2.text)
            bot_infos.append((info["name"], participant["elo"]))

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
        await context.send(embed=embed)

    @commands.command(name="top16")
    async def top16(self, context):
        await context.send("Not Implemented!")

    @commands.command(name="gg")
    async def gg(self, context):
        bot_name = str(context.message.content).split(" ")[1]
        bot_id = get_bot_id_by_name(bot_name)

        if bot_id == -1:
            await context.send(f"A bot with the name{bot_name} could not be located.")
        else:
            replay_pack_path = get_bot_replays(bot_id, False)
            if replay_pack_path == "":
                await context.send(f"Unable to download replays for {bot_name}. Please contact Turing's Ego#1850.")
            else:
                discord_file = discord.File(fp=replay_pack_path + ".zip", filename=f"{bot_name}_replays.zip")
                try:
                    await context.send(file=discord_file)
                    clean_up_archive(replay_pack_path)
                except Exception:
                    await context.send("replay pack too large!")


    @commands.command(name="getbetter")
    async def getbetter(self, context):
        bot_name = str(context.message.content).split(" ")[1]
        bot_id = get_bot_id_by_name(bot_name)
        if bot_id == -1:
            await context.send(f"A bot with the name{bot_name} could not be located.")
        else:
            replay_pack_path = get_bot_replays(bot_id, True)
            print(replay_pack_path)
            if replay_pack_path == "":
                await context.send(f"Unable to download replays for {bot_name}. Please contact Turing's Ego#1850.")
            else:
                discord_file = discord.File(fp=replay_pack_path + ".zip", filename=f"{bot_name}_loss_replays.zip")
                try:
                    await context.send(file=discord_file)
                    clean_up_archive(replay_pack_path)
                except Exception:
                    await context.send("replay pack too large!")

def setup(bot):
    bot.add_cog(Ladder(bot))