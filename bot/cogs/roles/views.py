import discord

class RoleMenuView(discord.ui.View):
    def __init__(self, roles_options: list[discord.SelectOption]):
        super().__init__(timeout=None)
        
        select = discord.ui.Select(
            custom_id="persistent_role_select",
            placeholder="Choose your roles...",
            min_values=0,
            max_values=len(roles_options),
            options=roles_options
        )
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        select = self.children[0]
        selected_role_ids = [int(v) for v in select.values]
        
        # We assume all roles in the options are the ones managed by this menu
        all_role_ids = [int(opt.value) for opt in select.options]
        
        member = interaction.user
        roles_to_add = [interaction.guild.get_role(r_id) for r_id in selected_role_ids if interaction.guild.get_role(r_id)]
        roles_to_remove = [interaction.guild.get_role(r_id) for r_id in all_role_ids if r_id not in selected_role_ids and interaction.guild.get_role(r_id) in member.roles]
        
        await member.add_roles(*roles_to_add, reason="Self-assigned roles")
        await member.remove_roles(*roles_to_remove, reason="Self-unassigned roles")
        
        await interaction.response.send_message("Your roles have been updated!", ephemeral=True)
