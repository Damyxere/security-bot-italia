import discord
from discord.ext import commands
from discord import app_commands
from firebase_admin import db

class RemoveCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="remove_blacklist", description="Rimuovi ID dalla blacklist")
    async def remove(self, interaction: discord.Interaction, target_id: str):
        if interaction.user.id != self.bot.owner_id:
            return await interaction.response.send_message("❌ Non puoi farlo.", ephemeral=True)
        
        # Prova a cancellare da entrambi i rami
        db.reference(f'blacklist/users/{target_id}').delete()
        db.reference(f'blacklist/servers/{target_id}').delete()
        
        await interaction.response.send_message(f"🗑️ ID `{target_id}` rimosso con successo.", ephemeral=True)

async def setup(bot): await bot.add_cog(RemoveCog(bot))