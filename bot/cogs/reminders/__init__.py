from bot.core.bot import DiscordServerOS
from bot.cogs.reminders.commands import ReminderCog

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(ReminderCog(bot))
