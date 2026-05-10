import discord
from discord.ext import commands, tasks
import firebase_admin
from firebase_admin import credentials
import os
import json
import asyncio
from aiohttp import web, ClientSession

# --- CONFIGURAZIONE VARIABILI AMBIENTALI ---
# Su Render, dovrai impostare queste chiavi nella sezione Environment
TOKEN = os.environ.get("DISCORD_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))
RENDER_URL = os.environ.get("RENDER_URL") # Es: https://tuo-bot.onrender.com
firebase_raw = os.environ.get("FIREBASE_JSON")

# --- INIZIALIZZAZIONE FIREBASE ---
if firebase_raw:
    try:
        cred_dict = json.loads(firebase_raw)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("🔥 [DATABASE] Firebase collegato con successo!")
    except Exception as e:
        print(f"❌ [ERRORE] Firebase JSON non valido: {e}")
else:
    print("⚠️ [ATTENZIONE] Variabile FIREBASE_JSON mancante!")

# --- TRUCCO ANTI-SLEEPING (WEB SERVER + SELF-PING) ---
async def home(request):
    return web.Response(text="Scorpion Security Bot is Online! 🚀")

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
    """Il bot chiama se stesso per non farsi spegnere da Render"""
    if not RENDER_URL or "onrender.com" not in RENDER_URL:
        return
    
    async with ClientSession() as session:
        try:
            async with session.get(RENDER_URL) as response:
                if response.status == 200:
                    print("💓 [SELF-PING] Bot svegliato con successo.")
        except Exception as e:
            print(f"⚠️ [SELF-PING] Errore: {e}")

# --- CLASSE BOT PRINCIPALE ---
class ScorpionBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        # Prefisso per i comandi pubblici (come !controlla)
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Caricamento automatico dei COGS (Blacklist e Backup)
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"✅ Modulo caricato: {filename}")
                except Exception as e:
                    print(f"❌ Errore caricamento {filename}: {e}")
        
        # Avvia il loop anti-sonno
        self_ping.start()

    async def on_ready(self):
        print(f"-----------------------------------")
        print(f"🦂 {self.user.name} ONLINE")
        print(f"👑 Owner ID: {self.owner_id}")
        print(f"-----------------------------------")
        # Sincronizza i comandi Slash (per /blacklist_user ecc.)
        await self.tree.sync()

# --- AVVIO ---
async def main():
    bot = ScorpionBot()
    bot.owner_id = OWNER_ID
    
    # Avvia web server e bot in parallelo
    await asyncio.gather(
        start_web_server(),
        bot.start(TOKEN)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass