import discord
from discord.ext import commands
import structlog
from bot.core.bot import DiscordServerOS
from bot.cogs.tempvoice.views import TempVoiceControlView
from bot.utils.formatters import info_embed

log = structlog.get_logger()

class TempVoiceListenersCog(commands.Cog):
    """Listeners for temporary voice channels."""

    __slots__ = ('bot',)

    def __init__(self, bot: DiscordServerOS):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        # Ignore deaf/mute changes
        if before.channel == after.channel:
            return

        # DB config lookup simulated
        # Logic to check if user joined the "Join to Create" channel
        join_to_create_channel_id = 0 # Replace with DB fetch
        
        if after.channel and after.channel.id == join_to_create_channel_id:
            category = after.channel.category
            try:
                new_channel = await category.create_voice_channel(
                    name=f"{member.display_name}'s Channel",
                    user_limit=after.channel.user_limit
                )
                await member.move_to(new_channel)
                
                embed = info_embed(
                    title="Voice Control Panel",
                    description="Use the buttons below to manage your temporary voice channel."
                )
                view = TempVoiceControlView(self.bot)
                
                # We could send the panel to a dedicated text channel or as a DM.
                # Assuming sending to a dedicated text channel in the same category if it exists,
                # else we don't send anything since it's a voice channel.
                # Actually, can send in the voice channel's chat!
                await new_channel.send(embed=embed, view=view)
                log.info("temp_voice_created", channel_id=new_channel.id, user_id=member.id)
            except discord.Forbidden:
                log.error("temp_voice_forbidden", guild_id=member.guild.id)
            except Exception as e:
                log.error("temp_voice_error", error=str(e))

        # Check if left channel is a temp channel and empty
        if before.channel and not before.channel.members:
            # Check if before.channel was a temp channel via DB
            # Simulated check
            is_temp = False # Replace with DB fetch
            if is_temp:
                try:
                    await before.channel.delete(reason="Temp channel empty")
                    log.info("temp_voice_deleted", channel_id=before.channel.id)
                except discord.Forbidden:
                    pass

async def setup(bot: DiscordServerOS) -> None:
    await bot.add_cog(TempVoiceListenersCog(bot))
