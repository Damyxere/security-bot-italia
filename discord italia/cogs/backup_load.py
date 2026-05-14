import discord
from discord.ext import commands
from discord import app_commands
from firebase_admin import db

class BackupLoad(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="backup_load", description="Carica un backup nel server")
    async def load(self, interaction: discord.Interaction):
        data = db.reference(f'backups/{interaction.user.id}').get()
        if not data: return await interaction.response.send_message("❌ Non hai backup da caricare.", ephemeral=True)

        view = LoadDropdownView(data)
        await interaction.response.send_message("📂 Seleziona il backup da ripristinare:", view=view, ephemeral=True)

class LoadDropdownView(discord.ui.View):
    def __init__(self, backups):
        super().__init__(timeout=60)
        options = [discord.SelectOption(label=name, value=name) for name in backups.keys()]
        self.add_item(LoadDropdown(options, backups))

class LoadDropdown(discord.ui.Select):
    def __init__(self, options, backups):
        super().__init__(placeholder="Scegli il backup...", options=options)
        self.backups = backups

    async def callback(self, it: discord.Interaction):
        b_data = self.backups[self.values[0]]
        await it.response.edit_message(content="🚀 Ripristino avviato... Pulizia canali.", view=None)
        
        for c in it.guild.channels:
            try: await c.delete()
            except: continue

        for cat in b_data['categories']:
            new_cat = await it.guild.create_category(cat['name'])
            for chan in cat['channels']:
                if chan['type'] == 'text': await it.guild.create_text_channel(chan['name'], category=new_cat)
                elif chan['type'] == 'voice': await it.guild.create_voice_channel(chan['name'], category=new_cat)
        
        await it.followup.send("✅ Ripristino completato con successo!")

async def setup(bot): await bot.add_cog(BackupLoad(bot))
