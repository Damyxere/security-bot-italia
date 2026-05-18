import discord
from discord.ext import commands
from discord import app_commands
from firebase_admin import db

class ScorpionPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Genera l'interfaccia visiva per l'amministratore del server
    def generate_status_embed(self, guild_name, status_data):
        def get_status_text(module_key):
            is_on = status_data.get(module_key, True) # Di default tutto attivo (True)
            return "🟢 **ATTIVO (ON)**" if is_on else "🔴 **DISATTIVATO (OFF)**"

        embed = discord.Embed(
            title="⚙️ PANNELLO DI GESTIONE SERVER",
            description=f"Configurazione moduli di sicurezza per: **{guild_name}**\n\nSeleziona una voce dal menu a tendina per cambiare lo stato di un modulo.",
            color=0x2f3136
        )
        
        embed.add_field(name="📂 MODULO BACKUP", value=get_status_text("status_backup"), inline=False)
        embed.add_field(name="⌨️ SISTEMA ANTI-SPAM", value=get_status_text("anti_spam"), inline=True)
        embed.add_field(name="🔗 PROTEZIONE ANTI-LINK", value=get_status_text("anti_link"), inline=True)
        embed.add_field(name="🚨 MOTORE ANTI-RAID", value=get_status_text("anti_raid"), inline=True)
        
        embed.set_footer(text="Scorpion Security Public Bot | Modifiche applicate solo a questo server")
        return embed

    @app_commands.command(name="panel", description="🎛️ Pannello amministratore per configurare i moduli del server")
    @app_commands.checks.has_permissions(administrator=True) # Solo gli admin del server possono usarlo
    async def panel_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild.id)
        
        # Recupera la configurazione specifica di QUESTO server da Firebase
        status_data = db.reference(f'settings/guilds/{guild_id}/modules').get()
        if not status_data:
            # Se il server usa il comando per la prima volta, crea il profilo su Firebase
            status_data = {"status_backup": True, "anti_spam": True, "anti_link": True, "anti_raid": True}
            db.reference(f'settings/guilds/{guild_id}/modules').set(status_data)

        embed = self.generate_status_embed(interaction.guild.name, status_data)
        view = PanelDropdownView(guild_id, status_data, self)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

# --- VIEW PER IL MENU A TENDINA ---
class PanelDropdownView(discord.ui.View):
    def __init__(self, guild_id, current_status, cog_reference):
        super().__init__(timeout=180) # Resta attivo per 3 minuti di inattività
        self.guild_id = guild_id
        self.status = current_status
        self.cog = cog_reference
        self.add_item(PanelDropdown(guild_id, current_status, cog_reference))

# --- LOGICA DEL MENU A TENDINA ---
class PanelDropdown(discord.ui.Select):
    def __init__(self, guild_id, current_status, cog_reference):
        self.guild_id = guild_id
        self.status = current_status
        self.cog = cog_reference

        options = [
            discord.SelectOption(label="📂 Switch modulo Backup", description="Attiva/Disattiva i backup in questo server", value="status_backup"),
            discord.SelectOption(label="⌨️ Switch modulo Anti-Spam", description="Attiva/Disattiva il blocco dello spam veloce", value="anti_spam"),
            discord.SelectOption(label="🔗 Switch modulo Anti-Link", description="Attiva/Disattiva il blocco degli inviti e link", value="anti_link"),
            discord.SelectOption(label="🚨 Switch modulo Anti-Raid", description="Attiva/Disattiva le difese dagli attacchi di massa", value="anti_raid")
        ]
        
        super().__init__(placeholder="Scegli una difesa per fare lo Switch...", options=options)

    async def callback(self, interaction: discord.Interaction):
        # Impedisce a chiunque non sia un amministratore di cliccare sul menu (sicurezza extra)
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Non hai i permessi per modificare questa configurazione.", ephemeral=True)

        selected_module = self.values[0]
        
        # Inverte lo stato locale (da True a False o viceversa)
        current_val = self.status.get(selected_module, True)
        self.status[selected_module] = not current_val
        
        # Aggiorna Firebase unicamente nella cartella di questo specifico server (guild_id)
        db.reference(f'settings/guilds/{self.guild_id}/modules').set(self.status)
        
        # Rigenera la grafica aggiornata ed effettua il refresh
        new_embed = self.cog.generate_status_embed(interaction.guild.name, self.status)
        await interaction.response.edit_message(embed=new_embed, view=PanelDropdownView(self.guild_id, self.status, self.cog))

async def setup(bot):
    await bot.add_cog(ScorpionPanel(bot))
