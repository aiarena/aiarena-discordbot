import discord
import os
import platform
import sys
from discord.ext.commands import Bot
try:
	import config
except ImportError:
	sys.exit("'config.py' not found! Please add it and try again.")

intents = discord.Intents.all()
intents.members = True
bot = Bot(command_prefix=config.BOT_PREFIX, intents=intents)

# The code in this even is executed when the bot is ready
@bot.event
async def on_ready():
	for extension in config.STARTUP_COGS:
		print(f"Loading extension '{extension}'")
		await bot.load_extension(extension)
	await bot.change_presence(activity=discord.Game("with electrons"))
	print(f"Logged in as: {bot.user.name}")
	print(f"Discord.py API version: {discord.__version__}")
	print(f"Python version: {platform.python_version()}")
	print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
	print("-------------------")

# Removes the default help command of discord.py to be able to create our custom help command.
bot.remove_command("help")

# The code in this event is executed every time someone sends a message, with or without the prefix
@bot.event
async def on_message(message):
	# Ignores if a command is being executed by a bot or by the bot itself
	if message.author == bot.user or message.author.bot:
		return
	if not message.content.startswith("!"):
		return
	await message.add_reaction(config.HOURGLASS_EMOJI)
	await bot.process_commands(message)


# The code in this event is executed every time a command has been *successfully* executed
@bot.event
async def on_command_completion(ctx: discord.ext.commands.Context):
	fullCommandName = ctx.command.qualified_name
	split = fullCommandName.split(" ")
	executedCommand = str(split[0])
	await ctx.message.remove_reaction(config.HOURGLASS_EMOJI, member=ctx.me)
	await ctx.message.add_reaction(config.GOOD_EMOJI)
	print(f"Executed {executedCommand} command in {ctx.guild.name} by {ctx.message.author} (ID: {ctx.message.author.id})")


# The code in this event is executed every time a valid commands catches an error
@bot.event
async def on_command_error(ctx: discord.ext.commands.Context, error):
	print(error)
	await ctx.message.remove_reaction(config.HOURGLASS_EMOJI, member=ctx.me)
	await ctx.message.add_reaction(config.FAILED_EMOJI)
	if isinstance(error, discord.ext.commands.errors.CommandNotFound):
		await ctx.message.reply("Command not found!")
	else:
		await ctx.message.reply(str(error.original))

# Run the bot with the token
bot.run(config.TOKEN)
