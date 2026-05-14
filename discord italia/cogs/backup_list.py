import discord
from discord.ext import commands
from discord import app_commands
from firebase_admin import db

class BackupList(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="backup_list", description="Mostra i tuoi backup salvati")
    async def list_backups(self, interaction: discord.Interaction):
        data = db.reference(f'backups/{interaction.user.id}').get()
        if not data: return await interaction.response.send_message("📭 Archivio vuoto.", ephemeral=True)

        embed = discord.Embed(title="📂 ARCHIVIO BACKUP SCORPION", color=0x00FBFF)
        for name in data.keys():
            embed.add_field(name="🖥️ Server", value=f"`{name}`", inline=False)
        
        footer = "Slot: Infiniti 🦂" if interaction.user.id == self.bot.owner_id else f"Slot: {len(data)}/2"
        embed.set_footer(text=footer)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot): await bot.add_cog(BackupList(bot))
