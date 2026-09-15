import discord
from discord.ext import commands
from bot.core.bot import DiscordServerOS
from bot.utils.formatters import info_embed

class SetupListenersCog(commands.Cog):
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        channel = None
        for c in guild.text_channels:
            if c.permissions_for(guild.me).send_messages:
                channel = c
                break
        
        if channel:
            embed = info_embed(
                title="Thanks for inviting me!",
                description="I can configure this server for you. Use `/setup start` to launch the interactive setup wizard."
            )
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="⚡ Start Setup", custom_id="start_setup_btn", style=discord.ButtonStyle.success))
            await channel.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        # Mark guild as inactive in DB
        pass
