import discord
import re
from datetime import datetime, timedelta, timezone
from discord import app_commands
from discord.ext import commands, tasks

from bot.core.bot import DiscordServerOS
from bot.services.giveaway_service import GiveawayService
from bot.cogs.giveaways.views import ActiveGiveawayView
from bot.utils.formatters import success_embed, error_embed, info_embed
from bot.utils.checks import is_admin, is_moderator

class GiveawayCog(commands.GroupCog, group_name="giveaway"):
    def __init__(self, bot: DiscordServerOS):
        self.bot = bot
        self.giveaway_service = GiveawayService(bot)
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    def parse_duration(self, duration_str: str) -> timedelta:
        regex = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
        parts = regex.match(duration_str)
        if not parts:
            return timedelta(minutes=10) # default
        parts_dict = parts.groupdict()
        time_params = {}
        for name, param in parts_dict.items():
            if param:
                time_params[name] = int(param)
        return timedelta(**time_params)

    @app_commands.command(name="create", description="Create a new giveaway")
    @app_commands.guild_only()
    @is_admin()
    async def create_giveaway(
        self, 
        interaction: discord.Interaction, 
        prize: str, 
        duration: str, 
        winners: int = 1, 
        channel: discord.TextChannel = None, 
        role: discord.Role = None, 
        description: str = None
    ):
        target_channel = channel or interaction.channel
        td = self.parse_duration(duration)
        if td.total_seconds() <= 0:
            await interaction.response.send_message(embed=error_embed("Invalid duration."), ephemeral=True)
            return

        ends_at = datetime.now(timezone.utc) + td

        giveaway = await self.giveaway_service.create_giveaway(
            guild_id=interaction.guild_id,
            channel_id=target_channel.id,
            host_id=interaction.user.id,
            prize=prize,
            description=description,
            winners_count=winners,
            ends_at=ends_at,
            required_role_id=role.id if role else None
        )

        embed = discord.Embed(
            title="🎉 GIVEAWAY 🎉",
            description=f"**Prize:** {prize}\n" + (f"{description}\n" if description else "") +
                        f"**Winners:** {winners}\n**Hosted by:** {interaction.user.mention}",
            color=discord.Color.purple(),
            timestamp=ends_at
        )
        if role:
            embed.add_field(name="Requirement", value=f"Must have {role.mention} role")
            
        embed.set_footer(text="Entries: 0 | Ends at")

        view = ActiveGiveawayView(self.bot, giveaway.id)
        msg = await target_channel.send(embed=embed, view=view)
        
        # update message id
        async with self.bot.db.session() as session:
            from sqlalchemy import select
            from bot.database.models.giveaways import Giveaway
            stmt = select(Giveaway).where(Giveaway.id == giveaway.id)
            res = await session.execute(stmt)
            gw = res.scalar_one()
            gw.message_id = msg.id
            await session.commit()

        await interaction.response.send_message(embed=success_embed(f"Giveaway created in {target_channel.mention}."), ephemeral=True)

    @app_commands.command(name="end", description="End a giveaway early")
    @app_commands.guild_only()
    @is_admin()
    async def end_giveaway(self, interaction: discord.Interaction, id: int):
        winners = await self.giveaway_service.end_giveaway(id)
        
        async with self.bot.db.session() as session:
            from sqlalchemy import select
            from bot.database.models.giveaways import Giveaway
            stmt = select(Giveaway).where(Giveaway.id == id)
            res = await session.execute(stmt)
            giveaway = res.scalar_one_or_none()

        if not giveaway:
            await interaction.response.send_message(embed=error_embed("Giveaway not found."), ephemeral=True)
            return

        channel = self.bot.get_channel(giveaway.channel_id)
        if channel and giveaway.message_id:
            try:
                msg = await channel.fetch_message(giveaway.message_id)
                embed = msg.embeds[0]
                embed.title = "🎉 GIVEAWAY ENDED 🎉"
                embed.color = discord.Color.default()
                await msg.edit(embed=embed, view=None)
                
                if winners:
                    winner_mentions = ", ".join(f"<@{w}>" for w in winners)
                    await channel.send(f"Congratulations {winner_mentions}! You won **{giveaway.prize}**!")
                else:
                    await channel.send(f"No one entered the giveaway for **{giveaway.prize}**.")
            except discord.NotFound:
                pass

        await interaction.response.send_message(embed=success_embed(f"Giveaway {id} ended."))

    @app_commands.command(name="reroll", description="Reroll giveaway winners")
    @app_commands.guild_only()
    @is_admin()
    async def reroll_giveaway(self, interaction: discord.Interaction, id: int, count: int = 1):
        winners = await self.giveaway_service.reroll_giveaway(id, count)
        if not winners:
            await interaction.response.send_message(embed=error_embed("Could not reroll giveaway (not enough entries or invalid ID)."), ephemeral=True)
            return

        async with self.bot.db.session() as session:
            from sqlalchemy import select
            from bot.database.models.giveaways import Giveaway
            stmt = select(Giveaway).where(Giveaway.id == id)
            res = await session.execute(stmt)
            giveaway = res.scalar_one_or_none()

        channel = self.bot.get_channel(giveaway.channel_id) if giveaway else interaction.channel
        
        winner_mentions = ", ".join(f"<@{w}>" for w in winners)
        if channel:
            await channel.send(f"🎉 New winner(s) for **{giveaway.prize if giveaway else 'Giveaway'}**: {winner_mentions}! Congratulations!")
            
        await interaction.response.send_message(embed=success_embed(f"Rerolled {count} winner(s)."))

    @app_commands.command(name="list", description="List active giveaways")
    @app_commands.guild_only()
    async def list_giveaways(self, interaction: discord.Interaction):
        giveaways = await self.giveaway_service.get_active_giveaways(interaction.guild_id)
        if not giveaways:
            await interaction.response.send_message(embed=info_embed("No active giveaways."), ephemeral=True)
            return
            
        desc = "\n".join(f"**ID {g.id}:** {g.prize} in <#{g.channel_id}> (Ends {discord.utils.format_dt(g.ends_at, 'R')})" for g in giveaways)
        await interaction.response.send_message(embed=info_embed(desc).set_author(name="Active Giveaways"))

    @tasks.loop(seconds=30)
    async def check_giveaways(self):
        async with self.bot.db.session() as session:
            from sqlalchemy import select
            from bot.database.models.giveaways import Giveaway
            
            now = datetime.now(timezone.utc)
            stmt = select(Giveaway).where(
                Giveaway.ended == False,
                Giveaway.ends_at <= now
            )
            result = await session.execute(stmt)
            ended_giveaways = result.scalars().all()
            
            for g in ended_giveaways:
                # End it
                winners = await self.giveaway_service.end_giveaway(g.id)
                channel = self.bot.get_channel(g.channel_id)
                if channel and g.message_id:
                    try:
                        msg = await channel.fetch_message(g.message_id)
                        embed = msg.embeds[0]
                        embed.title = "🎉 GIVEAWAY ENDED 🎉"
                        embed.color = discord.Color.default()
                        await msg.edit(embed=embed, view=None)
                        
                        if winners:
                            winner_mentions = ", ".join(f"<@{w}>" for w in winners)
                            await channel.send(f"Congratulations {winner_mentions}! You won **{g.prize}**!")
                        else:
                            await channel.send(f"No one entered the giveaway for **{g.prize}**.")
                    except discord.NotFound:
                        pass
