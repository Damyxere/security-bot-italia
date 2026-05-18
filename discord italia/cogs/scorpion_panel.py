import discord
from discord.ext import commands
from discord import app_commands
from firebase_admin import db

class ScorpionPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def generate_status_embed(self, guild_name, status_data):
        def get_status_text(module_key, default=True):
            is_on = status_data.get(module_key, default)
            return "🟢 **ATTIVO (ON)**" if is_on else "🔴 **DISATTIVATO (OFF)**"

        embed = discord.Embed(
            title="⚙️ CENTRAL SECURITY CONTROL PANEL",
            description=f"Pannello Amministratore Globale per: **{guild_name}**\n\nSeleziona una voce dal menu a tendina per invertire istantaneamente lo stato di un modulo di sicurezza.",
            color=0x2f3136
        )
        
        embed.add_field(name="📂 MODULO BACKUP", value=get_status_text("status_backup"), inline=True)
        embed.add_field(name="⌨️ SISTEMA ANTI-SPAM", value=get_status_text("anti_spam"), inline=True)
        embed.add_field(name="🔗 PROTEZIONE ANTI-LINK", value=get_status_text("anti_link"), inline=True)
        embed.add_field(name="🚨 MOTORE ANTI-RAID", value=get_status_text("anti_raid"), inline=True)
        embed.add_field(name="🛡️ ANTI-WEBHOOK HACK", value=get_status_text("anti_webhook"), inline=True)
        embed.add_field(name="🌙 LOCKDOWN NOTTURNO", value=get_status_text("night_lockdown", False), inline=True)
        embed.add_field(name="🚷 ANTI-ALT (Account Nuovi)", value=get_status_text("anti_alt", False), inline=True)
        embed.add_field(name="🎭 ANTI-SPAM REAZIONI", value=get_status_text("anti_reaction"), inline=True)
        embed.add_field(name="👁️ DETECTOR MESSAGGI EDITATI", value=get_status_text("anti_edit"), inline=True)
        
        embed.set_footer(text="Scorpion Security Systems | Protezione Multi-Livello Isolata")
        return embed

    @app_commands.command(name="panel", description="🎛️ Pannello amministratore per configurare la sicurezza globale del server")
    @app_commands.checks.has_permissions(administrator=True)
    async def panel_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild.id)
        
        status_data = db.reference(f'settings/guilds/{guild_id}/modules').get()
        if not status_data:
            status_data = {
                "status_backup": True, "anti_spam": True, "anti_link": True, 
                "anti_raid": True, "anti_webhook": True, "night_lockdown": False,
                "anti_alt": False, "anti_reaction": True, "anti_edit": True
            }
            db.reference(f'settings/guilds/{guild_id}/modules').set(status_data)

        embed = self.generate_status_embed(interaction.guild.name, status_data)
        view = PanelDropdownView(guild_id, status_data, self)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

class PanelDropdownView(discord.ui.View):
    def __init__(self, guild_id, current_status, cog_reference):
        super().__init__(timeout=180)
        self.guild_id = guild_id
        self.status = current_status
        self.cog = cog_reference
        self.add_item(PanelDropdown(guild_id, current_status, cog_reference))

class PanelDropdown(discord.ui.Select):
    def __init__(self, guild_id, current_status, cog_reference):
        self.guild_id = guild_id
        self.status = current_status
        self.cog = cog_reference

        options = [
            discord.SelectOption(label="📂 Modulo Backup", value="status_backup"),
            discord.SelectOption(label="⌨️ Modulo Anti-Spam", value="anti_spam"),
            discord.SelectOption(label="🔗 Modulo Anti-Link", value="anti_link"),
            discord.SelectOption(label="🚨 Modulo Anti-Raid", value="anti_raid"),
            discord.SelectOption(label="🛡️ Modulo Anti-Webhook", value="anti_webhook"),
            discord.SelectOption(label="🌙 Lockdown Notturno", value="night_lockdown"),
            discord.SelectOption(label="🚷 Anti-Alt Account", description="Blocca account creati da meno di 3 giorni", value="anti_alt"),
            discord.SelectOption(label="🎭 Anti-Spam Reazioni", description="Blocca il bombardamento di emoji", value="anti_reaction"),
            discord.SelectOption(label="👁️ Ghost Edit Detector", description="Blocca chi edita messaggi per inserire link/insulti", value="anti_edit")
        ]
        super().__init__(placeholder="Seleziona un modulo di sicurezza per fare lo Switch...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Permesso negato.", ephemeral=True)

        selected_module = self.values[0]
        
        # Gestione default corretta per i nuovi moduli disattivati all'inizio
        default_state = False if selected_module in ["night_lockdown", "anti_alt"] else True
        current_val = self.status.get(selected_module, default_state)
        
        self.status[selected_module] = not current_val
        db.reference(f'settings/guilds/{self.guild_id}/modules').set(self.status)
        
        new_embed = self.cog.generate_status_embed(interaction.guild.name, self.status)
        await interaction.response.edit_message(embed=new_embed, view=PanelDropdownView(self.guild_id, self.status, self.cog))

async def setup(bot): await bot.add_cog(ScorpionPanel(bot))
