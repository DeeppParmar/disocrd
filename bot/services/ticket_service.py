import time
from typing import Any, Tuple, List, Optional
from datetime import datetime, timezone, timedelta

import discord
import structlog
from sqlalchemy import select, update, func, desc

from bot.database.models.tickets import TicketConfig, Ticket, TicketMember
from bot.core.constants import TicketStatus

logger = structlog.get_logger(__name__)

class TicketService:
    __slots__ = ('bot',)

    def __init__(self, bot: Any) -> None:
        self.bot = bot

    async def create_ticket(self, guild: discord.Guild, creator_id: int, ticket_type: str, subject: Optional[str] = None) -> Tuple[Optional[discord.TextChannel], Optional[Ticket]]:
        config = await self.get_ticket_config(guild.id, ticket_type)
        if not config:
            return None, None
            
        async with self.bot.db.session() as session:
            count_stmt = select(func.count()).select_from(Ticket).where(
                Ticket.guild_id == guild.id,
                Ticket.creator_id == creator_id,
                Ticket.status == TicketStatus.OPEN
            )
            open_count = await session.scalar(count_stmt) or 0
            if open_count >= config.max_open_per_user:
                return None, None
                
            num_stmt = select(func.count()).select_from(Ticket).where(Ticket.guild_id == guild.id)
            ticket_number = (await session.scalar(num_stmt) or 0) + 1
            
            ticket = Ticket(
                guild_id=guild.id,
                ticket_number=ticket_number,
                creator_id=creator_id,
                ticket_type=ticket_type,
                subject=subject,
                status=TicketStatus.OPEN
            )
            session.add(ticket)
            await session.commit()
            
        category = guild.get_channel(config.category_id) if config.category_id else None
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.get_member(creator_id) or guild.get_role(creator_id): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        for role_id in config.staff_roles:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                
        channel_name = f"ticket-{ticket_number:04d}"
        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )
        
        async with self.bot.db.session() as session:
            stmt = update(Ticket).where(Ticket.id == ticket.id).values(channel_id=channel.id)
            await session.execute(stmt)
            await session.commit()
            ticket.channel_id = channel.id
            
        return channel, ticket

    async def close_ticket(self, guild: discord.Guild, ticket_id: int, closed_by: int) -> Optional[Ticket]:
        async with self.bot.db.session() as session:
            stmt = select(Ticket).where(Ticket.id == ticket_id)
            ticket = await session.scalar(stmt)
            if not ticket:
                return None
                
            ticket.status = TicketStatus.CLOSED
            ticket.closed_at = datetime.now(timezone.utc)
            ticket.closed_by = closed_by
            await session.commit()
            
            if ticket.channel_id:
                channel = guild.get_channel(ticket.channel_id)
                if channel:
                    member = guild.get_member(ticket.creator_id)
                    if member:
                        await channel.set_permissions(member, overwrite=None)
                        
            return ticket

    async def reopen_ticket(self, guild: discord.Guild, ticket_id: int) -> Optional[Ticket]:
        async with self.bot.db.session() as session:
            stmt = select(Ticket).where(Ticket.id == ticket_id)
            ticket = await session.scalar(stmt)
            if not ticket:
                return None
                
            ticket.status = TicketStatus.OPEN
            ticket.closed_at = None
            ticket.closed_by = None
            await session.commit()
            
            if ticket.channel_id:
                channel = guild.get_channel(ticket.channel_id)
                if channel:
                    member = guild.get_member(ticket.creator_id)
                    if member:
                        await channel.set_permissions(member, read_messages=True, send_messages=True)
                        
            return ticket

    async def claim_ticket(self, ticket_id: int, claimer_id: int) -> Optional[Ticket]:
        async with self.bot.db.session() as session:
            stmt = select(Ticket).where(Ticket.id == ticket_id)
            ticket = await session.scalar(stmt)
            if not ticket:
                return None
            ticket.claimed_by = claimer_id
            await session.commit()
            return ticket

    async def add_member(self, guild: discord.Guild, ticket_id: int, user_id: int) -> Optional[TicketMember]:
        async with self.bot.db.session() as session:
            stmt = select(Ticket).where(Ticket.id == ticket_id)
            ticket = await session.scalar(stmt)
            if not ticket:
                return None
                
            member = TicketMember(ticket_id=ticket_id, user_id=user_id)
            session.add(member)
            await session.commit()
            
            if ticket.channel_id:
                channel = guild.get_channel(ticket.channel_id)
                user = guild.get_member(user_id)
                if channel and user:
                    await channel.set_permissions(user, read_messages=True, send_messages=True)
            return member

    async def remove_member(self, guild: discord.Guild, ticket_id: int, user_id: int) -> None:
        async with self.bot.db.session() as session:
            stmt = select(Ticket).where(Ticket.id == ticket_id)
            ticket = await session.scalar(stmt)
            if not ticket:
                return
                
            del_stmt = select(TicketMember).where(TicketMember.ticket_id == ticket_id, TicketMember.user_id == user_id)
            tm = await session.scalar(del_stmt)
            if tm:
                await session.delete(tm)
                await session.commit()
                
            if ticket.channel_id:
                channel = guild.get_channel(ticket.channel_id)
                user = guild.get_member(user_id)
                if channel and user:
                    await channel.set_permissions(user, overwrite=None)

    async def get_open_tickets(self, guild_id: int, user_id: Optional[int] = None) -> List[Ticket]:
        async with self.bot.db.session() as session:
            stmt = select(Ticket).where(
                Ticket.guild_id == guild_id,
                Ticket.status == TicketStatus.OPEN
            )
            if user_id:
                stmt = stmt.where(Ticket.creator_id == user_id)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_ticket_by_channel(self, channel_id: int) -> Optional[Ticket]:
        async with self.bot.db.session() as session:
            stmt = select(Ticket).where(Ticket.channel_id == channel_id)
            return await session.scalar(stmt)

    async def generate_transcript(self, channel: discord.TextChannel, limit: int = 500) -> str:
        messages = [msg async for msg in channel.history(limit=limit, oldest_first=True)]
        lines = []
        for msg in messages:
            ts = msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
            lines.append(f"[{ts}] {msg.author}: {msg.content}")
            for attachment in msg.attachments:
                lines.append(f"[{ts}] {msg.author}: [Attachment: {attachment.url}]")
        return "\n".join(lines)

    async def check_inactivity(self, guild_id: int, hours: int = 48) -> List[Ticket]:
        async with self.bot.db.session() as session:
            threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
            stmt = select(Ticket).where(
                Ticket.guild_id == guild_id,
                Ticket.status == TicketStatus.OPEN,
                Ticket.updated_at <= threshold
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_ticket_config(self, guild_id: int, ticket_type: str) -> Optional[TicketConfig]:
        async with self.bot.db.session() as session:
            stmt = select(TicketConfig).where(
                TicketConfig.guild_id == guild_id,
                TicketConfig.ticket_type == ticket_type
            )
            return await session.scalar(stmt)

    async def create_ticket_config(self, guild_id: int, ticket_type: str, category_id: int, staff_roles: List[int], **kwargs: Any) -> TicketConfig:
        async with self.bot.db.session() as session:
            config = TicketConfig(
                guild_id=guild_id,
                ticket_type=ticket_type,
                category_id=category_id,
                staff_roles=staff_roles,
                **kwargs
            )
            session.add(config)
            await session.commit()
            return config
