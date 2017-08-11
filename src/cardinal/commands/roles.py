import logging

import discord
import discord.ext.commands as commands

from cardinal.commands import Cog
from cardinal.db import session_scope
from cardinal.db.roles import Role
from cardinal.utils import clean_prefix, channel_whitelisted

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Roles(Cog):
    def __init__(self, bot):
        super().__init__(bot)

    @commands.group(name='role', pass_context=True, no_pm=True)
    @commands.bot_has_permissions(manage_roles=True)
    @channel_whitelisted()
    async def roles(self, ctx: commands.Context):
        """Provides functionality for managing roles."""
        if ctx.invoked_subcommand is None:
            await self.bot.say(
                'Invalid command passed. Possible choices are "join", "leave",... \nPlease refer to `{}help {}` for further information.'
                .format(clean_prefix(ctx), ctx.command.qualified_name))
            return

    @roles.command(pass_context=True)
    async def join(self, ctx: commands.Context, *, role: discord.Role):
        """Adds the user to the specified role."""

        with session_scope() as session:
            if not session.query(Role).get(role.id):
                await self.bot.say('Role "{}" is not marked as a joinable role.'.format(role.name))
                return

        await self.bot.add_roles(ctx.message.author, role)

        await self.bot.say('User {user} joined role "{role}"'.format(user=ctx.message.author.mention, role=role.name))

    @roles.command(pass_context=True)
    async def leave(self, ctx: commands.Context, *, role: discord.Role):
        """Removes the user from the specified role."""

        with session_scope() as session:
            if not session.query(Role).get(role.id):
                await self.bot.say('Role "{}" cannot be left through this bot.'.format(role.name))
                return

        await self.bot.remove_roles(ctx.message.author, role)


        await self.bot.say('User {user} left role "{role}"'.format(user=ctx.message.author.mention, role=role.name))

    @roles.command(pass_context=True)
    async def list(self, ctx: commands.Context):
        """Lists the roles that can be joined through the bot."""

        with session_scope() as session:
            role_iter = (role.name for role in ctx.message.server.roles if session.query(Role).get(role.id))
            role_list = sorted(role_iter, key=lambda r: r.position)

        answer = 'Roles that can be joined through this bot:```\n'

        for role in role_list:
            answer += role
            answer += '\n'

        answer += '```'

        await self.bot.say(answer)

    @roles.command(pass_context=True)
    async def stats(self, ctx: commands.Context):
        """Shows the member count for each role."""

        with session_scope() as session:
            role_dict = dict((role, sum(1 for member in ctx.message.server.members if role in member.roles))
                             for role in ctx.message.server.roles if session.query(Role).get(role.id))

        em = discord.Embed(title='Role stats for ' + ctx.message.server.name, color=0x38CBF0)
        for role in sorted(role_dict.keys(), key=lambda r: r.position):
            em.add_field(name=role.name, value=role_dict[role])

        await self.bot.say(embed=em)

    @roles.command()
    @commands.has_permissions(manage_roles=True)
    async def add(self, *, role: discord.Role):
        """Marks a role as joinable."""

        with session_scope() as session:
            if session.query(Role).get(role.id):
                await self.bot.say('Role "{}" is already marked as a joinable role.'.format(role.name))
                return

            session.add(Role(role_id=role.id))

        await self.bot.say('Marked role "{}" as joinable.'.format(role.name))

    @roles.command()
    @commands.has_permissions(manage_roles=True)
    async def remove(self, *, role: discord.Role):
        """Removes a role from the list of joinable roles."""

        with session_scope() as session:
            role_db = session.query(Role).get(role.id)

            if not role_db:
                await self.bot.say('Role "{}" is not marked as a joinable role'.format(role.name))
                return

            session.delete(role_db)

        await self.bot.say('Removed role "{}" from list of joinable roles.'.format(role.name))

    @roles.command(pass_context=True)
    @commands.has_permissions(manage_roles=True)
    async def create(self, ctx: commands.Context, *, rolename: str):
        """Creates a new role and makes it joinable through the bot."""

        role = await self.bot.create_role(ctx.message.server, name=rolename)

        with session_scope() as session:
            session.add(Role(role_id=role.id))

        await self.bot.say('Created role "{}" and marked it as joinable.'.format(rolename))

    @roles.command()
    @commands.has_permissions(manage_roles=True)
    async def delete(self, *, role: discord.Role):
        """Deletes a role."""

        with session_scope() as session:
            role_db = session.query(Role).get(role.id)
            if role_db:
                session.delete(role_db)

        await self.bot.delete_role(role.server, role)
        await self.bot.say('Successfully deleted role "{}".'.format(role.name))
