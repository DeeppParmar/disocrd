from bot.core.bot import DiscordServerOS
from bot.cogs.starboard.commands import StarboardCog
from bot.cogs.starboard.listeners import StarboardListeners

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(StarboardCog(bot))
    await bot.add_cog(StarboardListeners(bot))
