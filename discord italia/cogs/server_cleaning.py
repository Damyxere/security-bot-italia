import discord
from discord.ext import commands
from discord import app_commands

class ServerCleaning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🧹 COMANDO: SVUOTA CANALE RAPIDO (Mantiene la configurazione)
    @app_commands.command(name="clear_chat", description="🧹 Cancella un numero specifico di messaggi nel canale corrente")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear_chat(self, interaction: discord.Interaction, quantita: int):
        if quantita < 1 or quantita > 100:
            return await interaction.response.send_message("❌ Puoi cancellare da 1 a 100 messaggi alla volta.", ephemeral=True)
            
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=quantita)
        await interaction.followup.send(f"✅ Rimossi con successo `{len(deleted)}` messaggi dal canale.", ephemeral=True)

    # 🚷 COMANDO: MASS KICK (Rimuove utenti senza ruoli entrati di recente)
    @app_commands.command(name="purge_ghosts", description="🚷 Espelle tutti gli utenti senza ruoli entrati nelle ultime 24 ore")
    @app_commands.checks.has_permissions(kick_members=True)
    async def purge_ghosts(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        now = discord.utils.utcnow()
        count = 0
        
        for member in interaction.guild.members:
            # Se è entrato da meno di 24 ore E ha un solo ruolo (quello base @everyone)
            if (now - member.joined_at).total_seconds() < 86400 and len(member.roles) == 1:
                try:
                    await member.kick(reason="Scorpion Bulk Purge: Pulizia account sospetti senza ruoli.")
                    count += 1
                except:
                    continue
                    
        await interaction.followup.send(f"🚷 Operazione completata. Espulsi `{count}` potenziali account fasulli.", ephemeral=True)

async def setup(bot): await bot.add_cog(ServerCleaning(bot))
