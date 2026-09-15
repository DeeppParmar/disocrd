from __future__ import annotations

from bot.core.bot import DiscordServerOS
from .commands import MembersCog

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(MembersCog(bot))
