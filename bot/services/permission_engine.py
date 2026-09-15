"""Permission evaluation and auditing service."""
import discord
from discord.ext import commands

PERMISSION_RISK_MAP: dict[str, str] = {
    "administrator": "Grants all permissions and bypasses channel overwrites.",
    "manage_guild": "Allows changing server settings, name, region, and bots.",
    "manage_roles": "Allows creating, deleting, and modifying roles below their own.",
    "manage_channels": "Allows creating, deleting, and modifying channels.",
    "kick_members": "Allows kicking members from the server.",
    "ban_members": "Allows banning members from the server.",
    "manage_webhooks": "Allows managing webhooks which can be used to send malicious messages.",
    "mention_everyone": "Allows mentioning @everyone and @here."
}

class PermissionEngine:
    __slots__ = ("bot",)

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def check_bot_permissions(self, guild: discord.Guild, required: discord.Permissions) -> tuple[bool, list[str]]:
        if guild.me is None:
            return False, ["bot_not_in_guild"]
        actual = guild.me.guild_permissions
        missing = [perm for perm, value in required if value and not getattr(actual, perm)]
        return len(missing) == 0, missing

    async def check_role_hierarchy(self, guild: discord.Guild, target_role: discord.Role) -> bool:
        if guild.me is None or guild.me.top_role is None:
            return False
        return guild.me.top_role > target_role

    async def compute_member_permissions(self, member: discord.Member, channel: discord.abc.GuildChannel) -> discord.Permissions:
        return channel.permissions_for(member)

    async def simulate_permissions(self, guild_id: int, user_id: int, channel_id: int) -> dict[str, bool]:
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            raise ValueError("Guild not found")
        member = guild.get_member(user_id)
        if member is None:
            raise ValueError("Member not found")
        channel = guild.get_channel(channel_id)
        if channel is None or not isinstance(channel, discord.abc.GuildChannel):
            raise ValueError("Channel not found")
        
        perms = channel.permissions_for(member)
        return {perm: value for perm, value in perms}

    async def audit_permissions(self, guild: discord.Guild) -> list[dict[str, str | int]]:
        issues: list[dict[str, str | int]] = []
        for role in guild.roles:
            for perm, desc in PERMISSION_RISK_MAP.items():
                if getattr(role.permissions, perm):
                    issues.append({
                        "role_id": role.id,
                        "role_name": role.name,
                        "permission": perm,
                        "risk": desc
                    })
        return issues

    def build_overwrites(self, policy_list: list[dict[str, discord.Permissions | discord.Object]]) -> dict[discord.Object, discord.PermissionOverwrite]:
        overwrites: dict[discord.Object, discord.PermissionOverwrite] = {}
        for policy in policy_list:
            target = policy["target"]
            allow = policy.get("allow", discord.Permissions())
            deny = policy.get("deny", discord.Permissions())
            if isinstance(target, discord.Object):
                allow_perms = allow if isinstance(allow, discord.Permissions) else discord.Permissions()
                deny_perms = deny if isinstance(deny, discord.Permissions) else discord.Permissions()
                overwrite = discord.PermissionOverwrite.from_pair(allow_perms, deny_perms)
                overwrites[target] = overwrite
        return overwrites
