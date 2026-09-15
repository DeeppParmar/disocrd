import discord
from discord.ui import View, Button

from bot.core.bot import DiscordServerOS
from bot.services.giveaway_service import GiveawayService
from bot.utils.formatters import success_embed, error_embed

class GiveawayEnterView(View):
    def __init__(self, bot: DiscordServerOS):
        super().__init__(timeout=None)
        self.bot = bot
        self.giveaway_service = GiveawayService(bot)

    @discord.ui.button(label="🎉 Enter Giveaway", style=discord.ButtonStyle.primary, custom_id="giveaway:enter:dynamic")
    async def enter_button(self, interaction: discord.Interaction, button: Button):
        # The custom_id format is giveaway:enter:{id}
        # In discord.py dynamic view custom_ids use a setup process, but we can extract it manually
        # Since button.custom_id is static in this simple implementation, let's assume it gets patched in dispatch or we extract id from embed footer/state
        
        # A more robust approach for discord.py 2.0 dynamic views
        pass

# Since discord.py dynamic items are a bit complex, let's use a simpler approach:
# Create a class factory or just parse the message id
class ActiveGiveawayView(View):
    def __init__(self, bot: DiscordServerOS, giveaway_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.giveaway_id = giveaway_id
        self.giveaway_service = GiveawayService(bot)
        
        btn = Button(label="🎉 Enter", style=discord.ButtonStyle.primary, custom_id=f"giveaway:enter:{giveaway_id}")
        btn.callback = self.enter_callback
        self.add_item(btn)

    async def enter_callback(self, interaction: discord.Interaction):
        # Re-fetch giveaway to check required role
        async with self.bot.db.session() as session:
            from sqlalchemy import select
            from bot.database.models.giveaways import Giveaway
            stmt = select(Giveaway).where(Giveaway.id == self.giveaway_id)
            result = await session.execute(stmt)
            giveaway = result.scalar_one_or_none()
            
            if not giveaway or giveaway.ended:
                await interaction.response.send_message("This giveaway has ended or doesn't exist.", ephemeral=True)
                return
                
            if giveaway.required_role_id:
                role = interaction.guild.get_role(giveaway.required_role_id)
                if role and role not in interaction.user.roles:
                    await interaction.response.send_message(f"You need the {role.mention} role to enter.", ephemeral=True)
                    return

        success = await self.giveaway_service.enter_giveaway(self.giveaway_id, interaction.user.id)
        if success:
            count = await self.giveaway_service.get_entry_count(self.giveaway_id)
            # Update the message with new count
            embed = interaction.message.embeds[0]
            embed.set_footer(text=f"Entries: {count} | Ends at")
            await interaction.message.edit(embed=embed)
            await interaction.response.send_message("You have entered the giveaway!", ephemeral=True)
        else:
            await interaction.response.send_message("You have already entered this giveaway.", ephemeral=True)
