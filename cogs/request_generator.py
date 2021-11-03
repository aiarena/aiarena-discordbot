import os, sys

if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config


def make_bot_info_request(bot_id: str) -> str:
    return config.BOT_INFO + bot_id + '/'


def make_top_ten_bots_request() -> str:
    return f"https://aiarena.net/api/competition-participations/?competition={config.SEASON}&ordering=-elo&limit=10"


def make_top_sixteen_bots_request() -> str:
    return f"https://aiarena.net/api/competition-participations/?competition={config.SEASON}&ordering=-elo&limit=16"

