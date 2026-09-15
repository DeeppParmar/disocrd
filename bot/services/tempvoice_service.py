from typing import Any, Dict, Optional
import discord
import structlog

logger = structlog.get_logger(__name__)

class TempVoiceService:
    __slots__ = ('bot', 'active_channels')

    def __init__(self, bot: Any) -> None:
        self.bot = bot
        self.active_channels: Dict[int, int] = {}

    async def create_temp_channel(self, guild: discord.Guild, member: discord.Member, category: Optional[discord.CategoryChannel]) -> Optional[discord.VoiceChannel]:
        name = f"{member.display_name}'s Channel"
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=True),
            member: discord.PermissionOverwrite(manage_channels=True, manage_permissions=True)
        }
        
        try:
            channel = await guild.create_voice_channel(name=name, category=category, overwrites=overwrites)
            self.active_channels[channel.id] = member.id
            if member.voice:
                await member.move_to(channel)
            return channel
        except discord.HTTPException:
            logger.error(f"Failed to create temp voice channel for {member.id} in {guild.id}")
            return None

    async def delete_if_empty(self, channel_id: int) -> bool:
        if channel_id not in self.active_channels:
            return False
            
        channel = self.bot.get_channel(channel_id)
        if channel and isinstance(channel, discord.VoiceChannel):
            if len(channel.members) == 0:
                try:
                    await channel.delete(reason="Temp voice channel empty")
                    del self.active_channels[channel_id]
                    return True
                except discord.HTTPException:
                    pass
        else:
            del self.active_channels[channel_id]
        return False

    async def set_limit(self, channel_id: int, limit: int) -> None:
        channel = self.bot.get_channel(channel_id)
        if channel and isinstance(channel, discord.VoiceChannel):
            try:
                await channel.edit(user_limit=limit)
            except discord.HTTPException:
                pass

    async def lock_channel(self, channel_id: int) -> None:
        channel = self.bot.get_channel(channel_id)
        if channel and isinstance(channel, discord.VoiceChannel):
            overwrite = channel.overwrites_for(channel.guild.default_role)
            overwrite.connect = False
            try:
                await channel.set_permissions(channel.guild.default_role, overwrite=overwrite)
            except discord.HTTPException:
                pass

    async def unlock_channel(self, channel_id: int) -> None:
        channel = self.bot.get_channel(channel_id)
        if channel and isinstance(channel, discord.VoiceChannel):
            overwrite = channel.overwrites_for(channel.guild.default_role)
            overwrite.connect = True
            try:
                await channel.set_permissions(channel.guild.default_role, overwrite=overwrite)
            except discord.HTTPException:
                pass

    async def is_owner(self, channel_id: int, user_id: int) -> bool:
        return self.active_channels.get(channel_id) == user_id
