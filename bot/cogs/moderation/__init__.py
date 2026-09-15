from __future__ import annotations

import discord
from discord.ext import commands

from bot.core.bot import DiscordServerOS
from .commands import ModerationCog

async def setup(bot: DiscordServerOS) -> None:
    """Load the Moderation cog."""
    await bot.add_cog(ModerationCog(bot))
