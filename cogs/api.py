import shutil

import discord, datetime, glob, json, os, random, requests, string, sys
from pathlib import Path
from discord.ext import commands

if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config

from cogs.exceptions import APIException


def get_bot_id_by_name(bot_name: str):
    request_url = f"{config.BOT_INFO}?name={bot_name}"
    response = requests.get(request_url, headers=config.AUTH)
    if response.status_code != 200:
        raise APIException(f"A bot with the name {bot_name} could not be located.", request_url, response)
    bot = json.loads(response.text)
    if len(bot["results"]) == 0:
        raise APIException(f"A bot with the name {bot_name} could not be located.", request_url, response)
    return bot["results"][0]["id"]


def get_bot_info(bot_id: str) -> dict:
    request_url = f"{config.BOT_INFO}{bot_id}/"
    response = requests.get(request_url, headers=config.AUTH)
    if response.status_code != 200:
        raise APIException(f"A bot with id {bot_id} could not be located.", request_url, response)
    return json.loads(response.text)


def download_replay(bot_name: str, bot_id: str, match_id: str, file_path: str) -> bool:
    request_url = f"{config.RESULTS}?match={match_id}"
    response = requests.get(request_url, headers=config.AUTH)
    if response.status_code != 200:
        raise APIException(f"Failed to get matches for bot id {bot_name}.", request_url, response)
    match_details = json.loads(response.text)
    if len(match_details["results"]) == 0:
        return False
    replay_file = match_details['results'][0]['replay_file']
    if replay_file not in (None, 'null'):
        replay = requests.get(replay_file, headers=config.AUTH)
        result = "won" if match_details["results"][0]['winner'] == bot_id else "loss"
        with open(os.path.join(file_path, str(match_details["results"][0]["bot1_name"]) + '_vs_' +
                                          str(match_details["results"][0]["bot2_name"]) + '___' +
                                          str(match_details["results"][0]["match"]) + "___" +
                                          result + '.SC2Replay'), 'wb') as f:
            f.write(replay.content)
    return True


def get_bot_matches(bot_name: str, bot_id: str, max_replays: int, only_losses: bool) -> str:
    letters = string.ascii_lowercase
    file_path = config.REPLAYS_DIR + ''.join(random.choice(letters) for i in range(10))
    Path(file_path).mkdir(parents=True, exist_ok=False)
    try:
        max_match = 999999
        num_replays = 0
        while num_replays < max_replays:
            request_url = f"{config.MATCH_PARTICPATION}?max_match={max_match}&bot={bot_id}&ordering=-match&limit=1"
            if only_losses:
                request_url += "?result=loss"
            response = requests.get(request_url, headers=config.AUTH)
            if response.status_code != 200:
                raise APIException(f"Failed to get matches for bot id {bot_name}.", request_url, response)
            participation = json.loads(response.text)
            match_id = participation['results'][0]['match']
            if download_replay(bot_name, bot_id, match_id, file_path):
                num_replays += 1
            max_match = match_id - 1
    except Exception as e:
        shutil.rmtree(file_path)
        raise e

    return file_path


def get_match_by_tag(tag_name: str, days: int) -> str:
    letters = string.ascii_lowercase
    file_path = config.REPLAYS_DIR + ''.join(random.choice(letters) for i in range(10))
    Path(file_path).mkdir(parents=True, exist_ok=False)
    today = datetime.datetime.now()
    days = datetime.timedelta(days=days + 1)
    start = today-days
    try:
        request_url = f"{config.MATCHES}?tags={tag_name}&ordering=-id"
        response = requests.get(request_url, headers=config.AUTH)
        if response.status_code != 200:
            raise APIException(f"Failed to get matches with tag {tag_name}.", request_url, response)
        matches = json.loads(response.text)
        for match in matches["results"]:
            year, month, day = match["created"].split('-')
            day = day.split('T')[0]
            match_date = datetime.datetime(int(year), int(month), int(day))
            if match_date > start:
                match_id = match["id"]
                download_replay(str(match["result"]["bot1_name"]), str(match["result"]["winner"]), match_id, file_path)
            else:
                # matches are in reverse order so the rest are too far in the past!
                break

    except Exception as e:
        shutil.rmtree(file_path)
        raise e

    # append {tag_name} to replay files
    for file in glob.glob(file_path + "/*.SC2Replay"):
        new_name = file.replace(".SC2Replay", f"___{tag_name}.SC2Replay")
        os.rename(file, new_name)

    return file_path
