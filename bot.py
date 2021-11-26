import discord, asyncio, os, platform, sys
from discord.ext.commands import Bot
from discord.ext import commands
if not os.path.isfile("config.py"):
	sys.exit("'config.py' not found! Please add it and try again.")
else:
	import config


bot = Bot(command_prefix=config.BOT_PREFIX)

message_hashes = {}

# The code in this even is executed when the bot is ready
@bot.event
async def on_ready():
	await bot.change_presence(activity=discord.Game("with electrons"))
	print(f"Logged in as {bot.user.name}")
	print(f"Discord.py API version: {discord.__version__}")
	print(f"Python version: {platform.python_version()}")
	print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
	print("-------------------")

# Removes the default help command of discord.py to be able to create our custom help command.
bot.remove_command("help")

if __name__ == "__main__":
	for extension in config.STARTUP_COGS:
		try:
			bot.load_extension(extension)
			extension = extension.replace("cogs.", "")
			print(f"Loaded extension '{extension}'")
		except Exception as e:
			exception = f"{type(e).__name__}: {e}"
			extension = extension.replace("cogs.", "")
			print(f"Failed to load extension {extension}\n{exception}")


# The code in this event is executed every time someone sends a message, with or without the prefix
@bot.event
async def on_message(message):
	# Ignores if a command is being executed by a bot or by the bot itself
	if message.author == bot.user or message.author.bot:
		return
	else:
		if message.content.startswith("!"):
			message_hashes[hash(message)] = message
			await message.add_reaction(config.HOURGLASS_EMOJI)
			await bot.process_commands(message)


# The code in this event is executed every time a command has been *successfully* executed
@bot.event
async def on_command_completion(ctx):
	fullCommandName = ctx.command.qualified_name
	split = fullCommandName.split(" ")
	executedCommand = str(split[0])
	user = discord.utils.get(bot.get_all_members(), id=config.BOT_DISCORD_ID)
	await message_hashes[hash(ctx.message)].remove_reaction(config.HOURGLASS_EMOJI, member=user)
	await message_hashes[hash(ctx.message)].add_reaction(config.GOOD_EMOJI)
	del message_hashes[hash(ctx.message)]
	print(f"Executed {executedCommand} command in {ctx.guild.name} by {ctx.message.author} (ID: {ctx.message.author.id})")


# The code in this event is executed every time a valid commands catches an error
@bot.event
async def on_command_error(context, error):
	print(error)

	user = discord.utils.get(bot.get_all_members(), id=config.BOT_DISCORD_ID)
	await message_hashes[hash(context.message)].remove_reaction(config.HOURGLASS_EMOJI, member=user)
	await message_hashes[hash(context.message)].add_reaction(config.FAILED_EMOJI)
	if isinstance(error, discord.ext.commands.errors.CommandNotFound):
		await message_hashes[hash(context.message)].reply("Command not found!")
	else:
		await message_hashes[hash(context.message)].reply(str(error.original))
	del message_hashes[hash(context.message)]

# Run the bot with the token
bot.run(config.TOKEN)
