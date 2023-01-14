import config


def make_bot_info_request(bot_id: str) -> str:
    return config.BOT_INFO + bot_id + '/'


def make_top_ten_bots_request() -> str:
    return f"https://aiarena.net/api/competition-participations/?competition={config.SEASON}&ordering=-elo&limit=10"


def make_top_sixteen_bots_request() -> str:
    return f"https://aiarena.net/api/competition-participations/?competition={config.SEASON}&ordering=-elo&limit=16"


def make_discord_users_request() -> str:
    return "https://aiarena.net/api/discord-users/"


def make_users_request() -> str:
    return "https://aiarena.net/api/users/?is_active=true&limit=99999999"

def make_unlinked_discord_uids_request() -> str:
    return "https://aiarena.net/api/patreon-unlinked-discord-uids/"


def make_active_bots_request() -> str:
    return f"https://aiarena.net/api/competition-participations/?competition={config.SEASON}"
