import discord, asyncio, random, string
from discord.ext import commands
from discord import app_commands
from firebase_admin import db

class BackupCreate(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="backup_create", description="Configura e crea un backup del server")
    async def create(self, interaction: discord.Interaction):
        if interaction.user.id != self.bot.owner_id:
            user_backups = db.reference(f'backups/{interaction.user.id}').get()
            if user_backups and len(user_backups) >= 2:
                return await interaction.response.send_message("❌ Limite di 2 backup raggiunto.", ephemeral=True)

        embed = discord.Embed(
            title="🛠️ CONFIGURAZIONE BACKUP",
            description="Seleziona cosa includere. Di default è tutto **ATTIVATO** (🟢).",
            color=0x2f3136
        )
        view = BackupConfigView(interaction.user.id, self.bot.owner_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class BackupConfigView(discord.ui.View):
    def __init__(self, user_id, owner_id):
        super().__init__(timeout=60)
        self.user_id, self.owner_id = user_id, owner_id
        self.settings = {"ruoli": True, "permessi": True, "canali": True, "categorie": True}

    def create_embed(self):
        emb = discord.Embed(title="🛠️ CONFIGURAZIONE BACKUP", color=0x2f3136)
        for k, v in self.settings.items():
            emb.add_field(name=k.upper(), value="🟢 ON" if v else "🔴 OFF", inline=True)
        return emb

    @discord.ui.button(label="Ruoli", style=discord.ButtonStyle.green)
    async def b1(self, it, bt):
        self.settings["ruoli"] = not self.settings["ruoli"]
        bt.style = discord.ButtonStyle.green if self.settings["ruoli"] else discord.ButtonStyle.red
        await it.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Permessi", style=discord.ButtonStyle.green)
    async def b2(self, it, bt):
        self.settings["permessi"] = not self.settings["permessi"]
        bt.style = discord.ButtonStyle.green if self.settings["permessi"] else discord.ButtonStyle.red
        await it.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Canali", style=discord.ButtonStyle.green)
    async def b3(self, it, bt):
        self.settings["canali"] = not self.settings["canali"]
        bt.style = discord.ButtonStyle.green if self.settings["canali"] else discord.ButtonStyle.red
        await it.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="🚀 AVVIA BACKUP", style=discord.ButtonStyle.primary, row=2)
    async def start(self, it, bt):
        await it.response.edit_message(content="⏳ Inizializzazione...", embed=None, view=None)
        
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        b_name = f"{it.guild.name}-{code}".replace(" ", "_")
        
        data = {"settings": self.settings, "categories": []}
        if self.settings["categorie"]:
            for cat in it.guild.categories:
                c_data = {"name": cat.name, "channels": []}
                if self.settings["canali"]:
                    c_data["channels"] = [{"name": c.name, "type": str(c.type)} for c in cat.channels]
                data["categories"].append(c_data)

        db.reference(f'backups/{self.user_id}/{b_name}').set(data)
        
        for i in range(10, 101, 30):
            await asyncio.sleep(0.4); await it.edit_original_response(content=f"📡 Salvataggio... {i}%")
        await it.edit_original_response(content=f"✅ Backup creato: `{b_name}`")

async def setup(bot): await bot.add_cog(BackupCreate(bot))
