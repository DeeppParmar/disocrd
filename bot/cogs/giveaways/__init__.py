from bot.core.bot import DiscordServerOS
from bot.cogs.giveaways.commands import GiveawayCog
from bot.cogs.giveaways.views import GiveawayEnterView

async def setup(bot: DiscordServerOS) -> None:
    bot.add_view(GiveawayEnterView(bot)) # add dynamic views later
    await bot.add_cog(GiveawayCog(bot))
