import discord
from discord.ext import commands, tasks
import structlog

from bot.core.bot import DiscordServerOS
from .views import TicketPanelView, TicketControlsView

logger = structlog.get_logger()

class TicketListenersCog(commands.Cog):
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot
        self.check_inactive_tickets.start()

    def cog_unload(self):
        self.check_inactive_tickets.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketPanelView())
        self.bot.add_view(TicketControlsView())
        logger.info("Registered persistent ticket views.")

    @tasks.loop(hours=1)
    async def check_inactive_tickets(self):
        """Auto-close inactive tickets."""
        logger.debug("Checking for inactive tickets...")
        # Business logic for inactive tickets goes here

    @check_inactive_tickets.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot: DiscordServerOS):
    await bot.add_cog(TicketListenersCog(bot))
