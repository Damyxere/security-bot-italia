import discord
import os
import json
import firebase_admin
from discord.ext import commands
from firebase_admin import credentials, db
from aiohttp import web
import asyncio

# --- WEB SERVER PER RENDER (Evita il Time Out) ---
async def handle(request):
    return web.Response(text="Scorpion Security Online")

async def run_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000) # Porta standard Render
    await site.start()

# --- CONFIGURAZIONE BOT ---
TOKEN = os.getenv('DISCORD_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))
FIREBASE_JSON = os.getenv('FIREBASE_JSON')
DATABASE_URL = os.getenv('FIREBASE_URL')

if not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(FIREBASE_JSON))
    firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})

class ScorpionBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        self.owner_id = OWNER_ID

    async def setup_hook(self):
        # Carica i Cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        
        # Avvia il server web per non far morire Render
        asyncio.create_task(run_web_server())
        
        await self.tree.sync()

bot = ScorpionBot()

@bot.event
async def on_ready():
    print(f"🦂 Scorpion Security ONLINE come {bot.user}")

bot.run(TOKEN)
