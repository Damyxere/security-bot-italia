import discord
from discord.ext import commands
from discord import app_commands
from firebase_admin import db
import datetime

class BlacklistModal(discord.ui.Modal, title='Registrazione Blacklist'):
    nome = discord.ui.TextInput(label='Nome', placeholder='Nome utente o server', required=True)
    target_id = discord.ui.TextInput(label='ID', placeholder='ID numerico', required=True)
    motivo = discord.ui.TextInput(label='Motivo', style=discord.TextStyle.paragraph, required=True)
    gravita = discord.ui.TextInput(label='Gravità', placeholder='Es: Alta', required=True)
    prove = discord.ui.TextInput(label='Prove', placeholder='Link screenshot/video', required=False)

    def __init__(self, tipo):
        super().__init__()
        self.tipo = tipo

    async def on_submit(self, interaction: discord.Interaction):
        ref = db.reference(f'blacklist/{self.tipo}/{self.target_id.value}')
        ref.set({
            'nome': self.nome.value, 'id': self.target_id.value,
            'motivo': self.motivo.value, 'gravita': self.gravita.value,
            'prove': self.prove.value, 'data': str(datetime.date.today()),
            'staffer': str(interaction.user.name)
        })
        await interaction.response.send_message(f"✅ {self.tipo.capitalize()} registrato!", ephemeral=True)

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

    @app_commands.command(name="registra_blacklist", description="Avvia registrazione")
    async def registra(self, interaction: discord.Interaction):
        if interaction.user.id != self.bot.owner_id:
            return await interaction.response.send_message("❌ Solo Owner!", ephemeral=True)
        await interaction.response.send_message("🛡️ Scegli cosa blacklistare:", view=BlacklistButtons(), ephemeral=True)

async def setup(bot): await bot.add_cog(RegisterCog(bot))