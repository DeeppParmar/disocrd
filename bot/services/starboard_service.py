import discord
from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert

from bot.database.models.starboard import StarboardConfig, StarboardEntry

class StarboardService:
    def __init__(self, bot):
        self.bot = bot

    async def get_config(self, guild_id: int) -> Optional[StarboardConfig]:
        async with self.bot.db.session() as session:
            stmt = select(StarboardConfig).where(StarboardConfig.guild_id == guild_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def setup(self, guild_id: int, channel_id: int, emoji: str = '⭐', threshold: int = 3) -> StarboardConfig:
        async with self.bot.db.session() as session:
            stmt = insert(StarboardConfig).values(
                guild_id=guild_id,
                channel_id=channel_id,
                emoji=emoji,
                threshold=threshold
            ).on_conflict_do_update(
                index_elements=['guild_id'],
                set_={'channel_id': channel_id, 'emoji': emoji, 'threshold': threshold}
            )
            await session.execute(stmt)
            await session.commit()
            
            # Fetch and return the updated/inserted config
            stmt = select(StarboardConfig).where(StarboardConfig.guild_id == guild_id)
            result = await session.execute(stmt)
            return result.scalar_one()

    async def process_reaction(
        self, 
        guild_id: int, 
        message_id: int, 
        channel_id: int, 
        author_id: int, 
        count: int
    ) -> Optional[StarboardEntry]:
        config = await self.get_config(guild_id)
        if not config or not config.enabled:
            return None

        async with self.bot.db.session() as session:
            stmt = select(StarboardEntry).where(StarboardEntry.original_message_id == message_id)
            result = await session.execute(stmt)
            entry = result.scalar_one_or_none()

            guild = self.bot.get_guild(guild_id)
            if not guild:
                return None
            
            starboard_channel = guild.get_channel(config.channel_id)
            if not starboard_channel:
                return None

            try:
                original_channel = guild.get_channel(channel_id)
                message = await original_channel.fetch_message(message_id)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException, AttributeError):
                return None

            if entry:
                entry.star_count = count
                if count < config.threshold:
                    if entry.starboard_message_id:
                        try:
                            star_msg = await starboard_channel.fetch_message(entry.starboard_message_id)
                            await star_msg.delete()
                        except discord.NotFound:
                            pass
                    await session.delete(entry)
                    await session.commit()
                    return None
                else:
                    if entry.starboard_message_id:
                        try:
                            star_msg = await starboard_channel.fetch_message(entry.starboard_message_id)
                            embed = await self.build_starboard_embed(message, count)
                            await star_msg.edit(content=f"{config.emoji} **{count}** | <#{channel_id}>", embed=embed)
                        except discord.NotFound:
                            # Starboard message was deleted manually, recreate
                            embed = await self.build_starboard_embed(message, count)
                            star_msg = await starboard_channel.send(content=f"{config.emoji} **{count}** | <#{channel_id}>", embed=embed)
                            entry.starboard_message_id = star_msg.id
                    await session.commit()
                    return entry
            else:
                if count >= config.threshold:
                    embed = await self.build_starboard_embed(message, count)
                    star_msg = await starboard_channel.send(content=f"{config.emoji} **{count}** | <#{channel_id}>", embed=embed)
                    
                    new_entry = StarboardEntry(
                        guild_id=guild_id,
                        original_message_id=message_id,
                        starboard_message_id=star_msg.id,
                        channel_id=channel_id,
                        author_id=author_id,
                        star_count=count
                    )
                    session.add(new_entry)
                    await session.commit()
                    return new_entry
                return None

    async def build_starboard_embed(self, message: discord.Message, count: int) -> discord.Embed:
        embed = discord.Embed(
            description=message.content,
            color=discord.Color.gold(),
            timestamp=message.created_at
        )
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url if message.author.display_avatar else None)
        
        if message.attachments:
            # Try to find an image
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith('image/'):
                    embed.set_image(url=attachment.url)
                    break
            
        embed.add_field(name="Source", value=f"[Jump to message]({message.jump_url})")
        return embed
