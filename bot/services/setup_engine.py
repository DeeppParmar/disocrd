"""Server setup orchestrator."""
import discord
from dataclasses import dataclass, field
from discord.ext import commands
from bot.services.role_manager import RoleManager
from bot.services.channel_manager import ChannelManager
from bot.utils.transactions import DiscordTransaction
from typing import Any

@dataclass
class RolePlan:
    name: str
    permissions: discord.Permissions
    color: discord.Color
    hoist: bool
    mentionable: bool

@dataclass
class CategoryPlan:
    name: str
    position: int
    overwrites: dict

@dataclass
class ChannelPlan:
    name: str
    type: str
    category: str | None
    topic: str
    overwrites: dict

@dataclass
class PermissionPlan:
    target: str
    allow: discord.Permissions
    deny: discord.Permissions

@dataclass
class SetupPlan:
    server_type: str
    roles_to_create: list[RolePlan] = field(default_factory=list)
    roles_to_update: list[RolePlan] = field(default_factory=list)
    categories_to_create: list[CategoryPlan] = field(default_factory=list)
    channels_to_create: list[ChannelPlan] = field(default_factory=list)
    channels_to_update: list[ChannelPlan] = field(default_factory=list)
    permissions_to_set: list[PermissionPlan] = field(default_factory=list)
    automod_rules: list[dict] = field(default_factory=list)
    features: dict[str, bool] = field(default_factory=dict)
    summary: dict[str, int] = field(default_factory=dict)

@dataclass
class SetupResult:
    success: bool
    completed_steps: int
    total_steps: int
    errors: list[str]
    operation_id: str
    created_resources: dict[str, Any]

class SetupEngine:
    __slots__ = ("bot", "role_manager", "channel_manager")

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.role_manager = RoleManager(bot)
        self.channel_manager = ChannelManager(bot)

    async def generate_plan(self, guild: discord.Guild, server_type: str, options: dict) -> SetupPlan:
        plan = SetupPlan(server_type=server_type)
        plan.summary = {"roles": 0, "channels": 0}
        return plan

    async def preview(self, guild: discord.Guild, plan: SetupPlan) -> discord.Embed:
        embed = discord.Embed(title="Setup Preview", description=f"Server Type: {plan.server_type}", color=discord.Color.blue())
        embed.add_field(name="Roles to Create", value=str(len(plan.roles_to_create)))
        embed.add_field(name="Channels to Create", value=str(len(plan.channels_to_create)))
        return embed

    async def execute(self, guild: discord.Guild, plan: SetupPlan, interaction: discord.Interaction) -> SetupResult:
        created = {}
        errors = []
        op_id = "op_" + str(guild.id)
        
        async with DiscordTransaction(f"setup_{guild.id}") as tx:
            try:
                for role_plan in plan.roles_to_create:
                    role = await self.role_manager.create_role(
                        guild, role_plan.name, role_plan.permissions, role_plan.color, role_plan.hoist, role_plan.mentionable, "Setup"
                    )
                    created[role.name] = role
                    tx.register_compensation(lambda r=role: r.delete(reason="Rollback"))
                
                await self.role_manager.reorder_roles(guild, [r.name for r in plan.roles_to_create])
                
                for cat_plan in plan.categories_to_create:
                    cat = await self.channel_manager.create_category(
                        guild, cat_plan.name, cat_plan.overwrites, cat_plan.position, "Setup"
                    )
                    created[cat.name] = cat
                    tx.register_compensation(lambda c=cat: c.delete(reason="Rollback"))
                
                for ch_plan in plan.channels_to_create:
                    cat = created.get(ch_plan.category) if ch_plan.category else None
                    if ch_plan.type == "text":
                        ch = await self.channel_manager.create_text_channel(
                            guild, ch_plan.name, cat, ch_plan.topic, 0, False, ch_plan.overwrites, "Setup"
                        )
                        created[ch.name] = ch
                        tx.register_compensation(lambda c=ch: c.delete(reason="Rollback"))
            except Exception as e:
                errors.append(str(e))
                raise e
            
        return SetupResult(
            success=len(errors) == 0,
            completed_steps=tx.completed_steps,
            total_steps=len(plan.roles_to_create) + len(plan.categories_to_create) + len(plan.channels_to_create),
            errors=errors,
            operation_id=op_id,
            created_resources=created
        )

    async def resume(self, guild: discord.Guild, operation_id: str) -> SetupResult:
        return SetupResult(True, 0, 0, [], operation_id, {})

    async def rollback(self, guild: discord.Guild, operation_id: str) -> None:
        pass
