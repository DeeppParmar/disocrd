import discord
from discord.ext import commands

from bot.core.bot import DiscordServerOS
from bot.services.afk_service import AFKService

class AFKListeners(commands.Cog):
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot
        self.afk_service = AFKService(bot)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # 1. Check if the author was AFK and just spoke
        afk = await self.afk_service.get_afk(message.guild.id, message.author.id)
        if afk:
            removed = await self.afk_service.remove_afk(message.guild.id, message.author.id)
            if removed:
                await message.reply(f"Welcome back {message.author.mention}, I've removed your AFK status.", delete_after=10)

        # 2. Check if mentioned users are AFK
        if message.mentions:
            mentioned_ids = [m.id for m in message.mentions if not m.bot]
            afk_statuses = await self.afk_service.check_mentions(message.guild.id, mentioned_ids)
            
            if afk_statuses:
                responses = []
                for status in afk_statuses:
                    responses.append(f"<@{status.user_id}> is AFK: {status.reason} (since {discord.utils.format_dt(status.set_at, 'R')})")
                
                if responses:
                    await message.reply("\n".join(responses), delete_after=15)
