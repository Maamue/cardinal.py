import logging

import discord
from discord.ext import commands

from ..context import Context
from .basecog import BaseCog

logger = logging.getLogger(__name__)


class Moderation(BaseCog):
    """
    A collection of general moderation commands to simplify the daily life of a mod.
    """

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx: Context, user: discord.Member, *, reason: str = None):
        """
        Kick a member from the current server.

        Parameters:
            - user: The member to kick, identified by mention, ID, or name.
            Must be a member of the server.
            - [optional] reason: The reason for kicking the user. Defaults to empty.

        Required context: Server

        Required permissions:
            - Kick Members

        Required bot permissions:
            - Kick Members
        """

        await user.kick(reason=reason)
        await ctx.send('User **{0}** ({0.id}) was kicked by {1}.'.format(user, ctx.author.mention))

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self,
                  ctx: Context,
                  user: discord.Member,
                  prune_days: int = 1,
                  *,
                  reason: str = None):
        """
        Ban a user from the current server

        Parameters:
            - user: The member to ban, identified by mention, ID, or name.
            - [optional] prune_days: The number of days
            for which the user's message should be pruned. Defaults to one day.
            - [optional] reason: The reason for banning the user. Defaults to empty.

        Required context: Server

        Required permissions:
            - Ban Members

        Required bot permissions:
            - Ban Members
        """

        if prune_days < 0:
            prune_days = 0
        elif prune_days > 7:
            prune_days = 7

        await user.ban(reason=reason, delete_message_days=prune_days)
        await ctx.send('User **{0}** ({0.id}) was banned by {1}.'.format(user, ctx.author.mention))
