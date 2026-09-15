from __future__ import annotations

from bot.core.bot import DiscordServerOS
from .commands import AutomationCog

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(AutomationCog(bot))
