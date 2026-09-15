from bot.cogs.server.commands import ServerCog

async def setup(bot):
    await bot.add_cog(ServerCog(bot))
