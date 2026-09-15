import discord
import re
from datetime import datetime, timedelta, timezone
from discord import app_commands
from discord.ext import commands, tasks

from bot.core.bot import DiscordServerOS
from bot.services.reminder_service import ReminderService
from bot.utils.formatters import success_embed, error_embed, info_embed

class ReminderCog(commands.GroupCog, group_name="reminders"):
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot
        self.reminder_service = ReminderService(bot)
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()

    def parse_duration(self, duration_str: str) -> timedelta:
        regex = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
        parts = regex.match(duration_str)
        if not parts:
            return timedelta(minutes=0)
        parts_dict = parts.groupdict()
        time_params = {}
        for name, param in parts_dict.items():
            if param:
                time_params[name] = int(param)
        return timedelta(**time_params)

    @app_commands.command(name="set", description="Set a reminder")
    async def set_reminder(self, interaction: discord.Interaction, time: str, message: str):
        td = self.parse_duration(time)
        if td.total_seconds() <= 0:
            await interaction.response.send_message(embed=error_embed("Invalid time format. Try '1h', '30m', '1d'."), ephemeral=True)
            return

        remind_at = datetime.now(timezone.utc) + td
        await self.reminder_service.create_reminder(
            guild_id=interaction.guild_id,
            channel_id=interaction.channel_id,
            user_id=interaction.user.id,
            message=message,
            remind_at=remind_at
        )

        await interaction.response.send_message(embed=success_embed(f"I will remind you about `{message}` {discord.utils.format_dt(remind_at, 'R')}."))

    @app_commands.command(name="list", description="Show your active reminders")
    async def list_reminders(self, interaction: discord.Interaction):
        reminders = await self.reminder_service.get_user_reminders(interaction.user.id)
        if not reminders:
            await interaction.response.send_message(embed=info_embed("You have no active reminders."), ephemeral=True)
            return

        desc = "\n".join(f"**ID {r.id}:** {discord.utils.format_dt(r.remind_at, 'R')} - {r.message}" for r in reminders)
        await interaction.response.send_message(embed=info_embed(desc).set_author(name="Your Reminders"), ephemeral=True)

    @app_commands.command(name="cancel", description="Cancel a reminder")
    async def cancel_reminder(self, interaction: discord.Interaction, id: int):
        success = await self.reminder_service.cancel_reminder(id, interaction.user.id)
        if success:
            await interaction.response.send_message(embed=success_embed(f"Reminder {id} cancelled."), ephemeral=True)
        else:
            await interaction.response.send_message(embed=error_embed(f"Reminder {id} not found or you don't own it."), ephemeral=True)

    @tasks.loop(seconds=30)
    async def check_reminders(self):
        due_reminders = await self.reminder_service.get_due_reminders()
        for r in due_reminders:
            try:
                channel = self.bot.get_channel(r.channel_id)
                if not channel:
                    user = self.bot.get_user(r.user_id)
                    if user:
                        await user.send(f"🔔 **Reminder:** {r.message}")
                else:
                    await channel.send(f"🔔 <@{r.user_id}> **Reminder:** {r.message}")
            except Exception:
                pass
            finally:
                await self.reminder_service.complete_reminder(r.id)

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()
