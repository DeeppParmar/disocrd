"""Role management service."""
import discord
from discord.ext import commands

class RoleMapping:
    logical_name: str
    role_id: int

class RoleManager:
    __slots__ = ("bot",)

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def create_role(self, guild: discord.Guild, name: str, permissions_preset: discord.Permissions, color: discord.Color, hoist: bool, mentionable: bool, reason: str) -> discord.Role:
        existing_roles = {role.name: role for role in guild.roles}
        if name in existing_roles:
            return existing_roles[name]
        return await guild.create_role(
            name=name,
            permissions=permissions_preset,
            color=color,
            hoist=hoist,
            mentionable=mentionable,
            reason=reason
        )

    async def delete_role(self, guild: discord.Guild, logical_name: str, reason: str) -> bool:
        role = discord.utils.get(guild.roles, name=logical_name)
        if role:
            await role.delete(reason=reason)
            return True
        return False

    async def sync_role(self, guild: discord.Guild, logical_name: str, **updates) -> discord.Role:
        role = discord.utils.get(guild.roles, name=logical_name)
        if not role:
            raise ValueError(f"Role {logical_name} not found")
        await role.edit(**updates)
        return role

    async def create_preset_roles(self, guild: discord.Guild, server_type: str) -> dict[str, discord.Role]:
        created = {}
        for role_name in ["Owner", "Admin", "Mod"]:
            created[role_name] = await self.create_role(
                guild, role_name, discord.Permissions.default(), discord.Color.default(), False, False, "Preset"
            )
        return created

    async def get_managed_roles(self, guild_id: int) -> list[RoleMapping]:
        return []

    async def reorder_roles(self, guild: discord.Guild, role_order: list[str]) -> None:
        positions: dict[discord.Role, int] = {}
        roles_by_name = {r.name: r for r in guild.roles}
        max_pos = len(role_order)
        for i, name in enumerate(role_order):
            if name in roles_by_name:
                positions[roles_by_name[name]] = max_pos - i
        if positions:
            await guild.edit_role_positions(positions)

    async def find_hierarchy_issues(self, guild: discord.Guild) -> list[dict]:
        return []
