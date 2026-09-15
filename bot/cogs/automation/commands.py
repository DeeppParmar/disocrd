import discord
from discord import app_commands
from discord.ext import commands, tasks
import structlog
from typing import Optional

from bot.core.bot import DiscordServerOS
from bot.utils.formatters import success_embed, info_embed
from bot.utils.checks import is_admin

log = structlog.get_logger()

class AutomationCog(commands.Cog):
    """Handles scheduled automated tasks."""
    
    __slots__ = ('bot',)

    def __init__(self, bot: DiscordServerOS):
        self.bot = bot
        self.task_loop.start()

    def cog_unload(self) -> None:
        self.task_loop.cancel()

    @tasks.loop(seconds=60)
    async def task_loop(self) -> None:
        """Polls DB for tasks due to run."""
        # Query DB for due tasks and execute them
        pass

    @task_loop.before_loop
    async def before_task_loop(self) -> None:
        await self.bot.wait_until_ready()

    automation_group = app_commands.Group(name="automation", description="Manage automated tasks")

    @automation_group.command(name="list", description="List scheduled tasks")
    @app_commands.guild_only()
    @is_admin()
    async def automation_list(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=info_embed("Scheduled Tasks", "List of tasks here..."), ephemeral=True)

    @automation_group.command(name="cancel", description="Cancel a scheduled task")
    @app_commands.guild_only()
    @is_admin()
    async def automation_cancel(self, interaction: discord.Interaction, id: int) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed(f"Task #{id} cancelled."), ephemeral=True)

    @automation_group.command(name="schedule", description="Create a scheduled task")
    @app_commands.choices(type=[
        app_commands.Choice(name="Message", value="message"),
        app_commands.Choice(name="Unban", value="unban"),
        app_commands.Choice(name="Role Add", value="role_add"),
        app_commands.Choice(name="Role Remove", value="role_remove"),
        app_commands.Choice(name="Backup", value="backup")
    ])
    @app_commands.guild_only()
    @is_admin()
    async def automation_schedule(self, interaction: discord.Interaction, type: str, when: str) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=success_embed(f"Task of type `{type}` scheduled for `{when}`."), ephemeral=True)
        log.info("task_scheduled", guild_id=interaction.guild_id, type=type, when=when)

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(AutomationCog(bot))
