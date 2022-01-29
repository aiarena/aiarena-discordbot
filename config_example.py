# rename file to `config.py` and fill in appropriate fields

# Can be multiple prefixes, like this: ("!", "?")
BOT_PREFIX = ("!")
TOKEN = "redacted"
API_TOKEN = "redacted"
APPLICATION_ID = "redacted"
OWNERS = [1234]
BLACKLIST = []
BOT_DISCORD_ID = 1234

AUTH = {'Authorization': f'Token {API_TOKEN}'}

STARTUP_COGS = [
    "cogs.help", "cogs.ladder", "cogs.urls"
]

REPLAYS_DIR = "replays/"

# urls
SEASON = 8
LADDER_RANKS = f"https://aiarena.net/api/competition-participations/?competition={SEASON}&ordering=-elo"
BOT_INFO = "https://aiarena.net/api/bots/"
USER_INFO = "https://aiarena.net/api/users/"
DISCORD_USER_INFO = "https://aiarena.net/api/discord-users/"
RESULTS = "https://aiarena.net/api/results/"
MATCHES = "https://aiarena.net/api/matches/"
MATCH_PARTICIPATION = "https://aiarena.net/api/match-participations/"

# role ids
AA_GUILD_ID = 430111136822722590
AA_BOT_AUTHOR_ID = 555372163788570635
AA_DONATOR_ID = 610982126669660218
SC2AI_GUILD_ID = 350289306763657218
SC2_BOT_AUTHOR_ID = 495250360055889946
SC2_DONATOR_ID = 912775653013741639

ROLES_IDS = {AA_GUILD_ID: [AA_BOT_AUTHOR_ID, AA_DONATOR_ID], SC2AI_GUILD_ID: [SC2_BOT_AUTHOR_ID, SC2_DONATOR_ID]}

# emojis
HOURGLASS_EMOJI = u"\u231b"
GOOD_EMOJI = u"\u2611"
FAILED_EMOJI = u"\u274C"
SMILEY = u"\u263A"