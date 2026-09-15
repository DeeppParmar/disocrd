from bot.cogs.setup.commands import SetupCog
from bot.cogs.setup.listeners import SetupListenersCog

async def setup(bot):
    await bot.add_cog(SetupCog(bot))
    await bot.add_cog(SetupListenersCog(bot))
