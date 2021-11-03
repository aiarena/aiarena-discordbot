# Can be multiple prefixes, like this: ("!", "?")
BOT_PREFIX = ("")
TOKEN = "redacted"
APPLICATION_ID = "redacted"
OWNERS = [55]
BLACKLIST = []

STARTUP_COGS = [
    "cogs.general", "cogs.help", "cogs.urls", "cogs.ladder"
]

REPLAYS_DIR = "replays/"

# urls
SEASON = 8
LADDER_RANKS = f"https://aiarena.net/api/competition-participations/?competition={SEASON}&ordering=-elo"
BOT_INFO = "https://aiarena.net/api/bots/"
MATCH_PARTICPATION = "https://aiarena.net/api/match-participations/"
RESULTS = "https://aiarena.net/api/results/"
MATCHES = "https://aiarena.net/api/matches/"

# emojis
GOOD_EMOJI = u"\u2611"
FAILED_EMOJI = u"\u274C"
SMILIE = u"\u263A"
