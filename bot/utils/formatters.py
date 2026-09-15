"""Discord formatting and pagination utilities."""
import datetime
from typing import Any
import discord

def create_embed(
    title: str | None = None,
    description: str | None = None,
    color: discord.Color | int | None = None,
    fields: list[dict[str, Any]] | None = None,
    footer: str | None = None,
    thumbnail: str | None = None,
    timestamp: datetime.datetime | None = None
) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color or discord.Color.default(), timestamp=timestamp)
    if fields:
        for field in fields:
            embed.add_field(name=field.get("name", "\u200b"), value=field.get("value", "\u200b"), inline=field.get("inline", False))
    if footer:
        embed.set_footer(text=footer)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    return embed

def success_embed(title: str, description: str) -> discord.Embed:
    return create_embed(title=title, description=description, color=discord.Color.green())

def error_embed(title: str, description: str) -> discord.Embed:
    return create_embed(title=title, description=description, color=discord.Color.red())

def warning_embed(title: str, description: str) -> discord.Embed:
    return create_embed(title=title, description=description, color=discord.Color.yellow())

def info_embed(title: str, description: str) -> discord.Embed:
    return create_embed(title=title, description=description, color=discord.Color.blue())

def progress_embed(title: str, completed: int, total: int, details: str) -> discord.Embed:
    percentage = int((completed / total) * 100) if total > 0 else 0
    bar_length = 10
    filled = int((percentage / 100) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    desc = f"{bar} {percentage}%\n\n{details}"
    return create_embed(title=title, description=desc, color=discord.Color.blurple())

def paginate(items: list[Any], per_page: int = 10) -> list[list[Any]]:
    return [items[i:i + per_page] for i in range(0, len(items), per_page)]

def format_permissions(perms: discord.Permissions) -> str:
    return ", ".join([perm.replace("_", " ").title() for perm, value in perms if value])

def format_duration(seconds: int) -> str:
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if days > 0: parts.append(f"{days}d")
    if hours > 0: parts.append(f"{hours}h")
    if minutes > 0: parts.append(f"{minutes}m")
    if seconds > 0 or not parts: parts.append(f"{seconds}s")
    return " ".join(parts)

def truncate(text: str, max_length: int = 1024) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def format_timestamp(dt: datetime.datetime, style: str = 'R') -> str:
    return f"<t:{int(dt.timestamp())}:{style}>"

class PaginatorView(discord.ui.View):
    __slots__ = ("embeds", "current_page", "author_id")

    def __init__(self, embeds: list[discord.Embed], author_id: int):
        super().__init__(timeout=180.0)
        self.embeds = embeds
        self.current_page = 0
        self.author_id = author_id
        self._update_buttons()

    def _update_buttons(self) -> None:
        self.prev_btn.disabled = self.current_page == 0
        self.next_btn.disabled = self.current_page == len(self.embeds) - 1
        self.counter_btn.label = f"Page {self.current_page + 1}/{len(self.embeds)}"

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You cannot use this.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, custom_id="prev")
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page = max(0, self.current_page - 1)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @discord.ui.button(label="Page 1/1", style=discord.ButtonStyle.secondary, disabled=True, custom_id="counter")
    async def counter_btn(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        pass

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, custom_id="next")
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page = min(len(self.embeds) - 1, self.current_page + 1)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
