import discord
from discord.ext import commands, tasks
import firebase_admin
from firebase_admin import credentials
import os
import json
import asyncio
from aiohttp import web, ClientSession

# --- 1. CONFIGURAZIONE VARIABILI ---
# Legge i dati dalle "Environment Variables" di Render
TOKEN = os.environ.get("DISCORD_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))
RENDER_URL = os.environ.get("RENDER_URL")
firebase_raw = os.environ.get("FIREBASE_JSON")

# --- 2. INIZIALIZZAZIONE FIREBASE (Senza file .json) ---
if firebase_raw:
    try:
        cred_dict = json.loads(firebase_raw)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("🔥 [DATABASE] Firebase collegato correttamente!")
    except Exception as e:
        print(f"❌ [ERRORE] JSON Firebase non valido: {e}")
else:
    print("⚠️ [ATTENZIONE] Variabile FIREBASE_JSON non trovata su Render!")

# --- 3. TRUCCO ANTI-SONNO (WEB SERVER + SELF-PING) ---
async def home(request):
    return web.Response(text="Scorpion Security is Active! 🦂")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", home)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 [WEB] Server finto attivo sulla porta {port}")

@tasks.loop(minutes=10)
async def self_ping():
    """Manda un segnale a se stesso per non far spegnere Render"""
    if not RENDER_URL or "onrender.com" not in RENDER_URL:
        return
    async with ClientSession() as session:
        try:
            async with session.get(RENDER_URL) as response:
                if response.status == 200:
                    print("💓 [PING] Il bot si è dato la sveglia.")
        except Exception as e:
            print(f"⚠️ [PING] Errore: {e}")

# --- 4. CLASSE BOT PRINCIPALE ---
class ScorpionBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Carica automaticamente tutti i file nella cartella /cogs
        # Se hai messo la Root Directory su Render, './cogs' è corretto
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"✅ Caricato modulo: {filename}")
                except Exception as e:
                    print(f"❌ Errore caricamento {filename}: {e}")
        
        # Avvia il loop per restare online
        self_ping.start()

    async def on_ready(self):
        print(f"-----------------------------------")
        print(f"🦂 {self.user.name} ONLINE")
        print(f"👑 Creatore: {self.owner_id}")
        print(f"-----------------------------------")
        # Sincronizza i comandi slash (/)
        await self.tree.sync()

# --- 5. ESECUZIONE ---
async def main():
    bot = ScorpionBot()
    bot.owner_id = OWNER_ID
    
    async with bot:
        # Avvia contemporaneamente il server web e il bot
        await asyncio.gather(
            start_web_server(),
            bot.start(TOKEN)
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
