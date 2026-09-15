"""Channel management service."""
import discord
from discord.ext import commands
from bot.utils.transactions import DiscordTransaction

class ChannelMapping:
    logical_name: str
    channel_id: int

class ChannelManager:
    __slots__ = ("bot",)

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def create_category(self, guild: discord.Guild, name: str, overwrites: dict, position: int, reason: str) -> discord.CategoryChannel:
        existing = discord.utils.get(guild.categories, name=name)
        if existing:
            return existing
        return await guild.create_category(name=name, overwrites=overwrites, position=position, reason=reason)

    async def create_text_channel(self, guild: discord.Guild, name: str, category: discord.CategoryChannel | None, topic: str, slowmode: int, nsfw: bool, overwrites: dict, reason: str) -> discord.TextChannel:
        existing = discord.utils.get(guild.text_channels, name=name)
        if existing:
            return existing
        return await guild.create_text_channel(name=name, category=category, topic=topic, slowmode_delay=slowmode, nsfw=nsfw, overwrites=overwrites, reason=reason)

    async def create_voice_channel(self, guild: discord.Guild, name: str, category: discord.CategoryChannel | None, bitrate: int, user_limit: int, overwrites: dict, reason: str) -> discord.VoiceChannel:
        existing = discord.utils.get(guild.voice_channels, name=name)
        if existing:
            return existing
        return await guild.create_voice_channel(name=name, category=category, bitrate=bitrate, user_limit=user_limit, overwrites=overwrites, reason=reason)

    async def create_forum_channel(self, guild: discord.Guild, name: str, category: discord.CategoryChannel | None, topic: str, tags: list[discord.ForumTag], overwrites: dict, reason: str) -> discord.ForumChannel:
        existing = discord.utils.get(guild.forums, name=name)
        if existing:
            return existing
        return await guild.create_forum(name=name, category=category, topic=topic, available_tags=tags, overwrites=overwrites, reason=reason)

    async def delete_channel(self, guild: discord.Guild, logical_name: str, reason: str) -> bool:
        channel = discord.utils.get(guild.channels, name=logical_name)
        if channel:
            await channel.delete(reason=reason)
            return True
        return False

    async def sync_channel(self, guild: discord.Guild, logical_name: str, **updates) -> discord.abc.GuildChannel:
        channel = discord.utils.get(guild.channels, name=logical_name)
        if not channel:
            raise ValueError("Channel not found")
        await channel.edit(**updates)
        return channel

    async def create_structure(self, guild: discord.Guild, structure: list[dict]) -> dict[str, discord.abc.GuildChannel]:
        created: dict[str, discord.abc.GuildChannel] = {}
        async with DiscordTransaction("create_structure") as tx:
            for item in structure:
                if item["type"] == "category":
                    cat = await self.create_category(guild, item["name"], item.get("overwrites", {}), item.get("position", 0), "Setup")
                    created[item["name"]] = cat
                    tx.register_compensation(lambda c=cat: c.delete(reason="Rollback"))
                elif item["type"] == "text":
                    cat = created.get(item.get("category_name")) if item.get("category_name") else None
                    if cat and isinstance(cat, discord.CategoryChannel):
                        ch = await self.create_text_channel(guild, item["name"], cat, item.get("topic", ""), item.get("slowmode", 0), item.get("nsfw", False), item.get("overwrites", {}), "Setup")
                        created[item["name"]] = ch
                        tx.register_compensation(lambda c=ch: c.delete(reason="Rollback"))
        return created

    async def get_managed_channels(self, guild_id: int) -> list[ChannelMapping]:
        return []

    async def lock_channel(self, channel: discord.abc.GuildChannel, reason: str) -> None:
        overwrites = channel.overwrites
        everyone = channel.guild.default_role
        overwrite = overwrites.get(everyone, discord.PermissionOverwrite())
        overwrite.send_messages = False
        await channel.set_permissions(everyone, overwrite=overwrite, reason=reason)

    async def unlock_channel(self, channel: discord.abc.GuildChannel, reason: str) -> None:
        overwrites = channel.overwrites
        everyone = channel.guild.default_role
        overwrite = overwrites.get(everyone, discord.PermissionOverwrite())
        overwrite.send_messages = None
        await channel.set_permissions(everyone, overwrite=overwrite, reason=reason)
