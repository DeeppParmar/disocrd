from bot.cogs.permissions.commands import PermissionsCog

async def setup(bot):
    await bot.add_cog(PermissionsCog(bot))
