import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class RaidDefense(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="panic_button", description="🚨 EMERGENZA: Blocca tutto e purga i nuovi membri")
    @app_commands.checks.has_permissions(administrator=True)
    async def panic(self, it: discord.Interaction):
        await it.response.defer(ephemeral=True)
        guild = it.guild
        
        # 1. Chiude il server
        for channel in guild.text_channels:
            await channel.set_permissions(guild.default_role, send_messages=False)
        
        # 2. Kicka chi è entrato negli ultimi 10 minuti (potenziali raider)
        count = 0
        now = discord.utils.utcnow()
        for member in guild.members:
            if (now - member.joined_at).total_seconds() < 600:
                await member.kick(reason="Protocollo PANIC attivato.")
                count += 1
        
        embed = discord.Embed(title="🆘 PROTOCOLLO PANIC: ATTIVATO", color=0xFF0000)
        embed.add_field(name="STATO SERVER", value="🔒 **LOCKDOWN TOTALE**", inline=False)
        embed.add_field(name="SOGGETTI ESPULSI", value=f"👤 `{count}` potenziali raider", inline=False)
        await it.followup.send(embed=embed)

    @app_commands.command(name="lockdown", description="Chiude o riapre il canale corrente")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lockdown(self, it: discord.Interaction, stato: bool):
        await it.guild.default_role.edit(permissions=it.guild.default_role.permissions.update(send_messages=not stato))
        msg = "🔒 Canale SIGILLATO" if stato else "🔓 Canale APERTO"
        await it.response.send_message(f"**{msg}**")

async def setup(bot): await bot.add_cog(RaidDefense(bot))
