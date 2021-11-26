import os, sys, discord
from discord.ext import commands
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config
from cogs.api import get_discord_users, get_patreon_users, get_bot_author_users


class Help(commands.Cog, name="help"):
    def __init__(self, bot):
        self.bot = bot

    async def clear_all_users(self, role):
        for member in role.members:
            await member.remove_roles(role)

    async def add_role(self, member_id: int, role):
        user = discord.utils.get(self.bot.get_all_members(), id=member_id)
        if user is not None:
            await user.add_roles(role)
        else:
            print(f"could not find user id {member_id} for this server.")

    @commands.command(name="update_roles")
    async def update_roles(self, context):
        guild_id = context.guild.id

        # clear all users in both roles
        # for role_id in config.ROLES_IDS[guild_id]:
        #     role = discord.utils.get(context.guild.roles, id=role_id)
        #     await self.clear_all_users(role)
        role = discord.utils.get(context.guild.roles, id=config.ROLES_IDS[guild_id][1])
        await self.clear_all_users(role)

        discord_users_dict = get_discord_users()

        patreon_users = get_patreon_users()
        patreon_users_discord = []
        patreon_users_discord_names = []
        for patreon_user in patreon_users:
            if patreon_user in discord_users_dict.keys():
                discord_name = await self.bot.fetch_user(discord_users_dict[patreon_user])
                patreon_users_discord_names.append(discord_name.name)
                patreon_users_discord.append(discord_users_dict[patreon_user])

        bot_authors = get_bot_author_users()
        bot_authors_discord = []
        bot_authors_discord_names = []
        for bot_author in bot_authors:
            if bot_author in discord_users_dict.keys():
                discord_name = await self.bot.fetch_user(discord_users_dict[bot_author])
                bot_authors_discord_names.append(discord_name.name)
                bot_authors_discord.append(discord_users_dict[bot_author])

        print(f"adding patreon role to users: {patreon_users_discord_names}")
        print(f"adding bot author roles to users: {bot_authors_discord_names}")

        for role_id, users in zip(config.ROLES_IDS[guild_id], [bot_authors_discord, patreon_users_discord]):
            role = discord.utils.get(context.guild.roles, id=role_id)
            for user_id in users:
                await self.add_role(user_id, role)

    @commands.command(name="help")
    async def help(self, context):
        # Note that commands made only for the owner of the bot are not listed here.
        embed = discord.Embed(
            title="Bot",
            description="List of commands are:",
            color=0x00FF00
        )
        embed.add_field(
            name="!invite",
            value="Get a discord invite link.",
            inline=False
        )
        embed.add_field(
            name="!top10",
            value="Top 10 ranked bots.",
            inline=False
        )
        embed.add_field(
            name="!top16",
            value="Top 16 ranked bots.",
            inline=False
        )
        embed.add_field(
            name="!bot <bot name>",
            value="Shouws Bot information.",
            inline=False)
        embed.add_field(
            name="!trello",
            value="Shows Trello board links.",
            inline=False
        )
        embed.add_field(
            name="!gs || !gettingstarted",
            value="Shows getting started infos.",
            inline=False
        )
        embed.add_field(
            name="!gg <bot_name> <num_days>  optional arguments: --loss --tag <tag_name>",
            value="Creates and uploads a replay pack of <bot_name>'s last <num_days> games, with various optional flags"
                  "to filters what replays are wanted.",
            inline=False
        )
        await context.reply(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
