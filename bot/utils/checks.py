"""Custom application command checks."""
import discord
from discord import app_commands

class MockGuildConfig:
    admin_role_ids: list[int] = []
    mod_role_ids: list[int] = []
    staff_role_ids: list[int] = []
    setup_completed: bool = True
    features: dict[str, bool] = {}

async def get_guild_config(guild_id: int) -> MockGuildConfig:
    return MockGuildConfig()

def is_admin() -> app_commands.check:
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return False
        if interaction.user.guild_permissions.administrator:
            return True
        config = await get_guild_config(interaction.guild.id)
        if any(role.id in config.admin_role_ids for role in interaction.user.roles):
            return True
        raise app_commands.CheckFailure("You must be an administrator to use this command.")
    return app_commands.check(predicate)

def is_moderator() -> app_commands.check:
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return False
        if interaction.user.guild_permissions.administrator:
            return True
        config = await get_guild_config(interaction.guild.id)
        valid_roles = set(config.admin_role_ids + config.mod_role_ids)
        if any(role.id in valid_roles for role in interaction.user.roles):
            return True
        raise app_commands.CheckFailure("You must be a moderator to use this command.")
    return app_commands.check(predicate)

def is_staff() -> app_commands.check:
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return False
        if interaction.user.guild_permissions.administrator:
            return True
        config = await get_guild_config(interaction.guild.id)
        valid_roles = set(config.admin_role_ids + config.mod_role_ids + config.staff_role_ids)
        if any(role.id in valid_roles for role in interaction.user.roles):
            return True
        raise app_commands.CheckFailure("You must be staff to use this command.")
    return app_commands.check(predicate)

def bot_has_guild_permissions(**perms: bool) -> app_commands.check:
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild is None or interaction.guild.me is None:
            return False
        guild_perms = interaction.guild.me.guild_permissions
        missing = [perm for perm, value in perms.items() if getattr(guild_perms, perm) != value]
        if not missing:
            return True
        raise app_commands.CheckFailure(f"Bot is missing required permissions: {', '.join(missing)}")
    return app_commands.check(predicate)

def require_setup() -> app_commands.check:
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild is None:
            return False
        config = await get_guild_config(interaction.guild.id)
        if config.setup_completed:
            return True
        raise app_commands.CheckFailure("Server setup is incomplete.")
    return app_commands.check(predicate)

def require_feature(feature_name: str) -> app_commands.check:
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild is None:
            return False
        config = await get_guild_config(interaction.guild.id)
        if config.features.get(feature_name, False):
            return True
        raise app_commands.CheckFailure(f"Feature '{feature_name}' is not enabled.")
    return app_commands.check(predicate)
