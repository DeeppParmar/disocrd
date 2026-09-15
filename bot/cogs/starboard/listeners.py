import discord
from discord.ext import commands

from bot.core.bot import DiscordServerOS
from bot.services.starboard_service import StarboardService

class StarboardListeners(commands.Cog):
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot
        self.starboard_service = StarboardService(bot)

    async def get_reaction_count(self, payload: discord.RawReactionActionEvent) -> int:
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return 0
        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return 0
            
        try:
            message = await channel.fetch_message(payload.message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return 0

        for reaction in message.reactions:
            if str(reaction.emoji) == str(payload.emoji):
                return reaction.count
        return 0

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if not payload.guild_id:
            return
            
        config = await self.starboard_service.get_config(payload.guild_id)
        if not config or not config.enabled:
            return
            
        if str(payload.emoji) != config.emoji:
            return
            
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return
        
        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception:
            return

        if message.author.id == payload.user_id and not config.self_star:
            # User self-starred and it's not allowed, remove the reaction
            await message.remove_reaction(payload.emoji, payload.member)
            return

        count = await self.get_reaction_count(payload)
        await self.starboard_service.process_reaction(
            payload.guild_id,
            payload.message_id,
            payload.channel_id,
            message.author.id,
            count
        )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if not payload.guild_id:
            return
            
        config = await self.starboard_service.get_config(payload.guild_id)
        if not config or not config.enabled:
            return
            
        if str(payload.emoji) != config.emoji:
            return
            
        count = await self.get_reaction_count(payload)
        
        # We need the author ID, but the message might be uncached
        # The service process_reaction function can fetch the message to get the author id if needed
        # We will pass 0 as author id, it doesn't matter for removal if the entry already exists
        await self.starboard_service.process_reaction(
            payload.guild_id,
            payload.message_id,
            payload.channel_id,
            0,
            count
        )
