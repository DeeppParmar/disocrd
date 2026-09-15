import discord
from discord.ui import View, Button
import structlog
from bot.core.bot import DiscordServerOS

log = structlog.get_logger()

class AutoModDashboardView(View):
    def __init__(self, bot: DiscordServerOS, guild_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id
        
        # Simulate loading status
        spam_status = True
        profanity_status = False

        self.add_item(Button(
            label="Spam Filter",
            style=discord.ButtonStyle.green if spam_status else discord.ButtonStyle.secondary,
            emoji="✅" if spam_status else "❌",
            custom_id="automod:toggle:spam"
        ))
        
        self.add_item(Button(
            label="Profanity Filter",
            style=discord.ButtonStyle.green if profanity_status else discord.ButtonStyle.secondary,
            emoji="✅" if profanity_status else "❌",
            custom_id="automod:toggle:profanity"
        ))
