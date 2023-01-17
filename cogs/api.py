import shutil

import datetime, glob, json, os, random, requests, string
from pathlib import Path
import config

from cogs.exceptions import APIException
from cogs.request_generator import make_discord_users_request, make_users_request, make_active_bots_request, \
    make_unlinked_discord_uids_request

# [name str] => bot id
bot_ids = {}

# [ai arena id] => [user name, True]
# [user name, discord linked = false]
# [discord id, discord linked = True]
author_names = {}


def get_patreon_users():
    request_url = make_users_request()
    response = requests.get(request_url, headers=config.AUTH)
    if response.status_code != 200:
        raise APIException("Could not users!", request_url, response)
    users = json.loads(response.text)["results"]
    patrean_users = []
    for user in users:
        if user["patreon_level"] != "none":
            patrean_users.append(user["id"])

    return patrean_users

def get_patreon_unlinked_uids():
    request_url = make_unlinked_discord_uids_request()
    response = requests.get(request_url, headers=config.AUTH)
    if response.status_code != 200:
        raise APIException("Could not get unlinked discord uids!", request_url, response)
    results = json.loads(response.text)["results"]
    discord_uids = []
    for uid in results:
        discord_uids.append(uid["discord_uid"])

    return discord_uids


def get_bot_author_users():
    request_url = make_active_bots_request()
    response = requests.get(request_url, headers=config.AUTH)
    if response.status_code != 200:
        raise APIException("Could not retrieve top 10 bots!", request_url, response)
    bots = json.loads(response.text)["results"]

    active_bot_ids = []
    for bot in bots:
        active_bot_ids.append(bot["bot"])
    active_bot_author_ids = set()
    for bot_id in active_bot_ids:
        request_url = f"{config.BOT_INFO}{bot_id}/"
        response = requests.get(request_url, headers=config.AUTH)
        if response.status_code != 200:
            raise APIException(f"A bot with id {bot_id} could not be located.", request_url, response)
        bot_info = json.loads(response.text)
        active_bot_author_ids.add(bot_info["user"])

    return active_bot_author_ids


def get_discord_users():
    request_url = make_discord_users_request()
    response = requests.get(request_url, headers=config.AUTH)
    if response.status_code != 200:
        raise APIException("Could not retrieve discord users", request_url, response)
    users = json.loads(response.text)["results"]
    discord_users = {}
    for user in users:
        discord_users[user["user"]] = user["uid"]

    return discord_users


def get_author_name_by_id(user_id: str):
    if user_id not in author_names.keys():
        request_url = f"{config.DISCORD_USER_INFO}?user={user_id}"
        response = requests.get(request_url, headers=config.AUTH)
        user = json.loads(response.text)
        if response.status_code != 200 or len(user["results"]) == 0:
            print(f"AI Arena id {user_id} does not have a linked discord account, "
                  f"falling back to getting ai arena name", request_url, response)
            request_url = f"{config.USER_INFO}/{user_id}"
            response = requests.get(request_url, headers=config.AUTH)
            if response.status_code != 200:
                raise APIException(f"An AI Arena user with id {user_id} could not be found. CRITICAL ERROR,"
                                   f"this ID is tied to a bot, but the id doesn't exist", request_url, response)
            user = json.loads(response.text)
            author_names[user_id] = [user["username"], False]
            print(author_names[user_id])
            return author_names[user_id]
        # discord id exists
        else:
            author_names[user_id] = [user["results"][0]["uid"], False]
            author_names[user_id][1] = True
    return author_names[user_id]


def get_bot_id_by_name(bot_name: str):
    if bot_name not in bot_ids.keys():
        request_url = f"{config.BOT_INFO}?name={bot_name}"
        response = requests.get(request_url, headers=config.AUTH)
        if response.status_code != 200:
            raise APIException(f"A bot with the name {bot_name} could not be located.", request_url, response)
        bot = json.loads(response.text)
        if len(bot["results"]) == 0:
            raise APIException(f"A bot with the name {bot_name} could not be located.", request_url, response)
        bot_ids[bot_name] = bot["results"][0]["id"]
    return bot_ids[bot_name]


def get_bot_info(bot_id: str) -> dict:
    request_url = f"{config.BOT_INFO}{bot_id}/"
    response = requests.get(request_url, headers=config.AUTH)
    if response.status_code != 200:
        raise APIException(f"A bot with id {bot_id} could not be located.", request_url, response)
    bot_info = json.loads(response.text)
    bot_info["author_info"] = get_author_name_by_id(bot_info["user"])
    return bot_info


def download_replay(replay_file: str, won: bool, file_path: str):
    if replay_file is None:
        return False
    result = "won"
    if not won:
        result = "loss"
    response = requests.get(replay_file, headers=config.AUTH)
    if response.status_code != 200:
        raise APIException(f"Failed to get replay {replay_file}.", replay_file, response)
    with open(os.path.join(file_path, replay_file.split('/')[-1] + "___" + result + '.SC2Replay'), 'wb') as f:
        f.write(response.content)
    return True


def get_match_by_id(match_id: str):
    request_url = f"{config.MATCHES}?id={match_id}"
    response = requests.get(request_url, headers=config.AUTH)
    if response.status_code != 200:
        raise APIException(f"Failed to match {match_id}.", request_url, response)
    return json.loads(response.text)["results"][0]


def get_elo_change(bot_name: str, bot_id: str, days: str):
    elo_change = 0

    year, month, day = days.split('-')
    day = day.split('T')[0]
    start = datetime.datetime(int(year), int(month), int(day))

    request_url = f"{config.MATCH_PARTICIPATION}?bot={bot_id}&ordering=-match&limit=250"
    response = requests.get(request_url, headers=config.AUTH)
    if response.status_code != 200:
        raise APIException(f"Failed to get matches for bot id {bot_name}.", request_url, response)
    matches = json.loads(response.text)["results"]
    for match in matches:
        # is the match recent enough?
        match_details = get_match_by_id(match["match"])
        year, month, day = match_details["created"].split('-')
        day = day.split('T')[0]
        match_date = datetime.datetime(int(year), int(month), int(day))

        if match_date < start:
            break

        if match["elo_change"] is not None:
            elo_change += match["elo_change"]

    return elo_change


def get_bot_matches(bot_name: str, bot_id: str, days: int, only_losses: bool, tag: str, limit: int) -> str:
    letters = string.ascii_lowercase
    file_path = config.REPLAYS_DIR + ''.join(random.choice(letters) for i in range(10))
    Path(file_path).mkdir(parents=True, exist_ok=False)

    today = datetime.datetime.now()
    days = datetime.timedelta(days=days + 1)
    start = today-days

    try:
        num_files = 0
        request_url = f"{config.MATCHES}?bot={bot_id}&ordering=-id&limit=250"
        response = requests.get(request_url, headers=config.AUTH)
        if response.status_code != 200:
            raise APIException(f"Failed to get matches for bot id {bot_name}.", request_url, response)
        matches = json.loads(response.text)["results"]
        for match in matches:
            # is the match recent enough?
            if match["started"] is None:
                continue
            year, month, day = match["started"].split('-')
            day = day.split('T')[0]
            match_date = datetime.datetime(int(year), int(month), int(day))
            if match_date < start:
                break
            # does the match have the appropriate tag?
            if match["tags"] and tag:
                has_tag = False
                for tag in match["tags"]:
                    if tag["tag_name"] != tag:
                        has_tag = True
                if not has_tag:
                    continue

            won = match["result"]["winner"] == bot_id
            if won and only_losses:
                continue
            # download the replay and check if we have enough replays to early exit
            if download_replay(match["result"]["replay_file"], won, file_path):
                num_files += 1
                if num_files >= limit:
                    break

    except Exception as e:
        shutil.rmtree(file_path)
        raise e

    if tag:
        # append {tag_name} to replay files
        for file in glob.glob(file_path + "/*.SC2Replay"):
            new_name = file.replace(".SC2Replay", f"___{tag}.SC2Replay")
            os.rename(file, new_name)
    print(num_files)
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
