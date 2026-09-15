import time
from typing import Any, List, Dict, Optional

import discord
import structlog

logger = structlog.get_logger(__name__)

class SecurityService:
    __slots__ = ('bot', 'join_tracker', 'lockdown_states', 'quarantined_roles')

    def __init__(self, bot: Any) -> None:
        self.bot = bot
        self.join_tracker: Dict[int, List[float]] = {}
        self.lockdown_states: Dict[int, Dict[int, Any]] = {}
        self.quarantined_roles: Dict[int, Dict[int, List[int]]] = {}

    async def check_raid(self, guild_id: int, join_timestamp: float) -> bool:
        if guild_id not in self.join_tracker:
            self.join_tracker[guild_id] = []
            
        self.join_tracker[guild_id].append(join_timestamp)
        
        window = join_timestamp - 30.0
        self.join_tracker[guild_id] = [ts for ts in self.join_tracker[guild_id] if ts > window]
        
        if len(self.join_tracker[guild_id]) > 10:
            return True
        return False

    async def activate_lockdown(self, guild: discord.Guild, reason: str, activated_by: int) -> Dict[str, Any]:
        locked = 0
        state = {}
        
        for channel in guild.text_channels:
            overwrite = channel.overwrites_for(guild.default_role)
            if overwrite.send_messages is not False:
                state[channel.id] = {'send_messages': overwrite.send_messages}
                overwrite.send_messages = False
                try:
                    await channel.set_permissions(guild.default_role, overwrite=overwrite, reason=f"Lockdown: {reason}")
                    locked += 1
                except discord.HTTPException:
                    pass
                    
        self.lockdown_states[guild.id] = state
        
        if hasattr(self.bot, 'services') and 'logging' in self.bot.services:
            await self.bot.services['logging'].log_security_event(
                guild.id, 'lockdown_activated', 'high', {'reason': reason, 'channels_locked': locked, 'activator': activated_by}
            )
            
        return {"locked_channels": locked}

    async def deactivate_lockdown(self, guild: discord.Guild, deactivated_by: int) -> Dict[str, Any]:
        restored = 0
        state = self.lockdown_states.pop(guild.id, {})
        
        for channel_id, perms in state.items():
            channel = guild.get_channel(channel_id)
            if channel and isinstance(channel, discord.TextChannel):
                overwrite = channel.overwrites_for(guild.default_role)
                overwrite.send_messages = perms.get('send_messages')
                if overwrite.is_empty():
                    await channel.set_permissions(guild.default_role, overwrite=None, reason="Lockdown deactivated")
                else:
                    await channel.set_permissions(guild.default_role, overwrite=overwrite, reason="Lockdown deactivated")
                restored += 1
                
        if hasattr(self.bot, 'services') and 'logging' in self.bot.services:
            await self.bot.services['logging'].log_security_event(
                guild.id, 'lockdown_deactivated', 'low', {'channels_restored': restored, 'deactivator': deactivated_by}
            )
            
        return {"restored_channels": restored}

    async def quarantine_member(self, guild: discord.Guild, member: discord.Member, reason: str) -> None:
        role_ids = [r.id for r in member.roles if r.id != guild.id and not r.is_integration() and not r.is_premium_subscriber()]
        
        if guild.id not in self.quarantined_roles:
            self.quarantined_roles[guild.id] = {}
        self.quarantined_roles[guild.id][member.id] = role_ids
        
        quarantine_role = discord.utils.get(guild.roles, name="Quarantined")
        if not quarantine_role:
            try:
                quarantine_role = await guild.create_role(name="Quarantined", reason="Quarantine system setup")
                for channel in guild.channels:
                    await channel.set_permissions(quarantine_role, send_messages=False, read_messages=False, connect=False)
            except discord.HTTPException:
                pass
                
        roles_to_keep = [r for r in member.roles if r.id not in role_ids]
        if quarantine_role:
            roles_to_keep.append(quarantine_role)
            
        try:
            await member.edit(roles=roles_to_keep, reason=f"Quarantined: {reason}")
        except discord.HTTPException:
            pass
            
        if hasattr(self.bot, 'services') and 'logging' in self.bot.services:
            await self.bot.services['logging'].log_security_event(
                guild.id, 'member_quarantined', 'medium', {'target_id': member.id, 'reason': reason}
            )

    async def unquarantine_member(self, guild: discord.Guild, member: discord.Member) -> None:
        role_ids = self.quarantined_roles.get(guild.id, {}).pop(member.id, [])
        roles_to_add = [guild.get_role(r_id) for r_id in role_ids if guild.get_role(r_id)]
        
        quarantine_role = discord.utils.get(guild.roles, name="Quarantined")
        roles_to_keep = [r for r in member.roles if r.id != (quarantine_role.id if quarantine_role else 0)]
        
        try:
            await member.edit(roles=roles_to_keep + roles_to_add, reason="Unquarantined")
        except discord.HTTPException:
            pass
            
        if hasattr(self.bot, 'services') and 'logging' in self.bot.services:
            await self.bot.services['logging'].log_security_event(
                guild.id, 'member_unquarantined', 'low', {'target_id': member.id}
            )

    async def get_lockdown_state(self, guild_id: int) -> Optional[Dict[int, Any]]:
        return self.lockdown_states.get(guild_id)

    async def scan_for_threats(self, guild: discord.Guild) -> List[Dict[str, Any]]:
        threats = []
        now = time.time()
        for member in guild.members:
            if (now - member.created_at.timestamp()) < (7 * 86400):
                threats.append({'type': 'new_account', 'target': member.id, 'details': 'Account created less than 7 days ago'})
        return threats
