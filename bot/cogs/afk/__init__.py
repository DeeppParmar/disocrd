from bot.core.bot import DiscordServerOS
from bot.cogs.afk.commands import AFKCog
from bot.cogs.afk.listeners import AFKListeners

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(AFKCog(bot))
    await bot.add_cog(AFKListeners(bot))
