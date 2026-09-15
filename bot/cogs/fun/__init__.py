from bot.core.bot import DiscordServerOS
from bot.cogs.fun.commands import FunCog

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(FunCog(bot))
