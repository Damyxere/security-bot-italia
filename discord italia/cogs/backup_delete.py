import discord
from discord.ext import commands
from discord import app_commands
from firebase_admin import db

class BackupDelete(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="backup_delete", description="Elimina un backup")
    async def delete(self, interaction: discord.Interaction, nome_backup: str):
        ref = db.reference(f'backups/{interaction.user.id}/{nome_backup}')
        if not ref.get(): return await interaction.response.send_message("❌ Backup non trovato.", ephemeral=True)

        view = ConfirmDelete(ref, nome_backup)
        await interaction.response.send_message(f"⚠️ Vuoi eliminare `{nome_backup}`?", view=view, ephemeral=True)

class ConfirmDelete(discord.ui.View):
    def __init__(self, ref, name):
        super().__init__(); self.ref, self.name = ref, name

    @discord.ui.button(label="CONFERMA", style=discord.ButtonStyle.danger)
    async def confirm(self, it, bt):
        self.ref.delete()
        await it.response.edit_message(content=f"🗑️ `{self.name}` eliminato.", view=None)

async def setup(bot): await bot.add_cog(BackupDelete(bot))
