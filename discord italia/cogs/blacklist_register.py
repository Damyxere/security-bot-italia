import discord
from discord.ext import commands
from discord import app_commands
from firebase_admin import db
import datetime

class BlacklistModal(discord.ui.Modal, title='Registrazione Blacklist'):
    nome = discord.ui.TextInput(label='Nome', placeholder='Nome utente o server', required=True)
    target_id = discord.ui.TextInput(label='ID', placeholder='ID numerico', required=True)
    motivo = discord.ui.TextInput(label='Motivo', style=discord.TextStyle.paragraph, required=True)
    gravita = discord.ui.TextInput(label='Gravità', placeholder='Bassa/Media/Alta', required=True)
    prove = discord.ui.TextInput(label='Prove', placeholder='Link agli screenshot', required=False)

    def __init__(self, tipo):
        super().__init__()
        self.tipo = tipo

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            ref = db.reference(f'blacklist/{self.tipo}/{self.target_id.value}')
            ref.set({
                'nome': str(self.nome.value),
                'id': str(self.target_id.value),
                'motivo': str(self.motivo.value),
                'gravita': str(self.gravita.value),
                'prove': str(self.prove.value) if self.prove.value else "Nessuna",
                'data': str(datetime.date.today()),
                'staffer': str(interaction.user.name)
            })
            await interaction.followup.send(f"✅ {self.tipo[:-1]} aggiunto alla blacklist!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Errore: {e}", ephemeral=True)

class BlacklistButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="User", style=discord.ButtonStyle.danger)
    async def user_btn(self, interaction: discord.Interaction, btn: discord.ui.Button):
        await interaction.response.send_modal(BlacklistModal(tipo="users"))

    @discord.ui.button(label="Server", style=discord.ButtonStyle.secondary)
    async def server_btn(self, interaction: discord.Interaction, btn: discord.ui.Button):
        await interaction.response.send_modal(BlacklistModal(tipo="servers"))

class RegisterCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="registra_blacklist", description="Avvia registrazione blacklist")
    async def registra(self, interaction: discord.Interaction):
        if interaction.user.id != self.bot.owner_id:
            return await interaction.response.send_message("❌ Solo l'Owner può usare questo comando.", ephemeral=True)
        await interaction.response.send_message("🛡️ **Scorpion Security**\nScegli cosa registrare:", view=BlacklistButtons(), ephemeral=True)

async def setup(bot): await bot.add_cog(RegisterCog(bot))
