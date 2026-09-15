from bot.core.bot import DiscordServerOS
from bot.cogs.tags.commands import TagCog

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(TagCog(bot))
