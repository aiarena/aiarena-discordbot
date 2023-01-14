import discord
from discord.ext import commands
import config
from cogs.api import get_discord_users, get_patreon_users, get_bot_author_users, get_patreon_unlinked_uids


class Help(commands.Cog, name="help"):
    def __init__(self, bot):
        self.bot = bot

    async def clear_all_users(self, role):
        for member in role.members:
            await member.remove_roles(role)

    async def add_role(self, member_id: int, role):
        user = discord.utils.get(self.bot.get_all_members(), id=member_id, guild=role.guild)
        if user is not None:
            await user.add_roles(role)
        else:
            print(f"could not find user id {member_id} for this server.")

    @commands.command(name="update_roles")
    async def update_roles(self, context: discord.ext.commands.Context):
        guild = context.guild

        # clear all users in donator role
        role = discord.utils.get(context.guild.roles, id=config.ROLES_IDS[guild.id][1])
        await self.clear_all_users(role)

        discord_users_dict = get_discord_users()

        patreon_users = get_patreon_users()
        patreon_users_discord = []
        for patreon_user in patreon_users:
            if patreon_user in discord_users_dict.keys():
                patreon_users_discord.append(discord_users_dict[patreon_user])

        patreon_users_discord += get_patreon_unlinked_uids()

        bot_authors = get_bot_author_users()
        bot_authors_discord = []
        for bot_author in bot_authors:
            if bot_author in discord_users_dict.keys():
                bot_authors_discord.append(discord_users_dict[bot_author])

        print(guild)
        for role_id, users in zip(config.ROLES_IDS[guild.id], [bot_authors_discord, patreon_users_discord]):
            role = discord.utils.get(context.guild.roles, id=role_id)
            print(role)
            for user_id in users:
                member = context.message.guild.get_member(int(user_id))
                if member is not None:
                    # member will be None if the user is not in the guild
                    await member.add_roles(role)

    @commands.command(name="help")
    async def help(self, context: discord.ext.commands.Context):
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
            value="Shows Bot information.",
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


async def setup(bot):
    await bot.add_cog(Help(bot))
