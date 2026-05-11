import discord
import os
import json
import firebase_admin
from discord.ext import commands
from firebase_admin import credentials

# Caricamento configurazioni da Render
TOKEN = os.getenv('DISCORD_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))
FIREBASE_JSON = os.getenv('FIREBASE_JSON')
DATABASE_URL = os.getenv('FIREBASE_URL') # Assicurati di aver aggiunto questa su Render!

# Inizializzazione Firebase
if not firebase_admin._apps:
    cred_dict = json.loads(FIREBASE_JSON)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': DATABASE_URL
    })

class ScorpionBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        self.owner_id = OWNER_ID

    async def setup_hook(self):
        # Carica automaticamente tutti i file dentro la cartella cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        
        await self.tree.sync()
        print(f"✅ Comandi sincronizzati per {self.user}")

bot = ScorpionBot()

@bot.event
async def on_ready():
    print(f"🦂 Scorpion Security ONLINE | Loggato come {bot.user}")

bot.run(TOKEN)
