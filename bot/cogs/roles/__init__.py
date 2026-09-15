from bot.cogs.roles.commands import RoleCog

async def setup(bot):
    await bot.add_cog(RoleCog(bot))
