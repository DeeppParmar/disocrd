import discord
from discord import app_commands
from discord.ext import commands

from bot.core.bot import DiscordServerOS
from bot.services.tag_service import TagService
from bot.utils.formatters import success_embed, error_embed, info_embed

class TagCog(commands.GroupCog, group_name="tag"):
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot
        self.tag_service = TagService(bot)

    async def tag_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if not interaction.guild:
            return []
        tags = await self.tag_service.search_tags(interaction.guild_id, current)
        return [app_commands.Choice(name=tag.name, value=tag.name) for tag in tags][:25]

    @app_commands.command(name="get", description="Get a tag's content")
    @app_commands.guild_only()
    @app_commands.autocomplete(name=tag_autocomplete)
    async def get_tag(self, interaction: discord.Interaction, name: str):
        tag = await self.tag_service.get_tag(interaction.guild_id, name)
        if not tag:
            await interaction.response.send_message(embed=error_embed("Tag not found."), ephemeral=True)
            return
        await interaction.response.send_message(tag.content)

    @app_commands.command(name="create", description="Create a new tag")
    @app_commands.guild_only()
    async def create_tag(self, interaction: discord.Interaction, name: str, content: str):
        tag = await self.tag_service.create_tag(interaction.guild_id, name, content, interaction.user.id)
        if not tag:
            await interaction.response.send_message(embed=error_embed(f"A tag named `{name}` already exists."), ephemeral=True)
            return
        await interaction.response.send_message(embed=success_embed(f"Tag `{name}` created."))

    @app_commands.command(name="edit", description="Edit an existing tag")
    @app_commands.guild_only()
    @app_commands.autocomplete(name=tag_autocomplete)
    async def edit_tag(self, interaction: discord.Interaction, name: str, content: str):
        # We assume the user owns it or is admin, but since we didn't add ownership check, we'll just check if it exists
        tag = await self.tag_service.update_tag(interaction.guild_id, name, content)
        if not tag:
            await interaction.response.send_message(embed=error_embed("Tag not found."), ephemeral=True)
            return
        await interaction.response.send_message(embed=success_embed(f"Tag `{name}` updated."))

    @app_commands.command(name="delete", description="Delete a tag")
    @app_commands.guild_only()
    @app_commands.autocomplete(name=tag_autocomplete)
    async def delete_tag(self, interaction: discord.Interaction, name: str):
        success = await self.tag_service.delete_tag(interaction.guild_id, name)
        if not success:
            await interaction.response.send_message(embed=error_embed("Tag not found."), ephemeral=True)
            return
        await interaction.response.send_message(embed=success_embed(f"Tag `{name}` deleted."))

    @app_commands.command(name="list", description="List all tags")
    @app_commands.guild_only()
    async def list_tags(self, interaction: discord.Interaction):
        tags = await self.tag_service.list_tags(interaction.guild_id)
        if not tags:
            await interaction.response.send_message(embed=info_embed("No tags found for this server."), ephemeral=True)
            return
        
        description = "\n".join(f"**{t.name}** (uses: {t.uses})" for t in tags)
        await interaction.response.send_message(embed=info_embed(description).set_author(name="Server Tags"))

    @app_commands.command(name="info", description="Get info about a tag")
    @app_commands.guild_only()
    @app_commands.autocomplete(name=tag_autocomplete)
    async def tag_info(self, interaction: discord.Interaction, name: str):
        # We need to fetch without incrementing uses, or just use get_tag and ignore the side effect
        # Using search to just get the model without triggering the get_tag side effect
        tags = await self.tag_service.search_tags(interaction.guild_id, name)
        tag = next((t for t in tags if t.name.lower() == name.lower()), None)
        if not tag:
            await interaction.response.send_message(embed=error_embed("Tag not found."), ephemeral=True)
            return
        
        embed = info_embed(f"Info for tag **{tag.name}**")
        embed.add_field(name="Author", value=f"<@{tag.author_id}>", inline=True)
        embed.add_field(name="Uses", value=str(tag.uses), inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(tag.created_at, "R"), inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="search", description="Search tags")
    @app_commands.guild_only()
    async def search_tags_cmd(self, interaction: discord.Interaction, query: str):
        tags = await self.tag_service.search_tags(interaction.guild_id, query)
        if not tags:
            await interaction.response.send_message(embed=info_embed("No tags found matching query."), ephemeral=True)
            return
        
        description = "\n".join(f"**{t.name}**" for t in tags)
        await interaction.response.send_message(embed=info_embed(description).set_author(name=f"Search Results: {query}"))
