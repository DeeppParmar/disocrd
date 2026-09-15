import discord
from discord.ext import commands
import structlog

from bot.core.bot import DiscordServerOS
from bot.core.constants import Colors

logger = structlog.get_logger()

class WelcomeListenersCog(commands.Cog):
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Retrieve channel and config from DB here
        pass

async def setup(bot: DiscordServerOS):
    await bot.add_cog(WelcomeListenersCog(bot))
