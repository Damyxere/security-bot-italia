import discord
from discord.ext import commands, tasks
import datetime
from firebase_admin import db

class AdvancedDefense(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_night_lockdown.start() # Avvia il ciclo di controllo orario automatico

    def cog_unload(self):
        self.check_night_lockdown.cancel()

    # 🛡️ 1. GESTIONE ANTI-WEBHOOK (Rileva la creazione di un webhook)
    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):
        guild_id = str(channel.guild.id)
        
        # Controlla se il modulo è attivo per questo server
        is_active = db.reference(f'settings/guilds/{guild_id}/modules/anti_webhook').get()
        if not is_active: return

        # Trova chi ha creato il webhook controllando i log del server
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.webhook_create):
            # Se a crearlo è stato un utente non amministratore o un utente sospetto
            if not entry.user.guild_permissions.administrator and entry.user.id != self.bot.user.id:
                # Elimina tutti i webhook in quel canale per sicurezza
                webhooks = await channel.webhooks()
                for wh in webhooks:
                    await wh.delete(reason="Scorpion Anti-Webhook: Rilevato potenziale exploit")
                
                # Punisce il creatore abusivo togliendogli i ruoli o kickandolo
                try:
                    await entry.user.kick(reason="Scorpion Security: Creazione non autorizzata di Webhook")
                    await channel.send(f"🚨 **SECURITY ALERT**: Eliminato Webhook abusivo creato da {entry.user.mention}. Il soggetto è stato espulso.")
                except:
                    pass

    # 🌙 2. GESTIONE LOCKDOWN NOTTURNO (Controlla ogni minuto)
    @tasks.loop(minutes=1)
    async def check_night_lockdown(self):
        now = datetime.datetime.now()
        ora_corrente = now.hour

        # Cicla su tutti i server in cui è presente il bot
        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            is_active = db.reference(f'settings/guilds/{guild_id}/modules/night_lockdown').get()
            if not is_active: continue

            # Fascia oraria di blocco: dalle 23:00 alle 05:59
            if ora_corrente >= 23 or ora_corrente < 6:
                # Se siamo nell'orario notturno, toglie il permesso di inviare messaggi a @everyone
                for channel in guild.text_channels:
                    # Controlla se @everyone ha ancora i permessi attivi per scrivere
                    perms = channel.overwrites_for(guild.default_role)
                    if perms.send_messages is not False:
                        perms.send_messages = False
                        await channel.set_permissions(guild.default_role, overwrite=perms, reason="Scorpion Automatic Night Lockdown")
                        
                        # Invia un messaggio di avviso solo la prima volta (es. alle 23:00)
                        if now.minute == 0 and ora_corrente == 23:
                            await channel.send("🌙 **SISTEMA**: Attivato l'Auto-Lockdown Notturno. La scrittura in questo canale è temporaneamente sospesa fino alle 06:00.")
            else:
                # Fuori dall'orario notturno, ripristina la scrittura (se era bloccata)
                for channel in guild.text_channels:
                    perms = channel.overwrites_for(guild.default_role)
                    if perms.send_messages is False:
                        perms.send_messages = None # Ripristina il permesso predefinito del ruolo
                        await channel.set_permissions(guild.default_role, overwrite=perms, reason="Scorpion Night Lockdown Terminata")
                        
                        if now.minute == 0 and ora_corrente == 6:
                            await channel.send("☀️ **SISTEMA**: Lockdown notturno terminata. I canali sono stati riaperti. Buona giornata!")

async def setup(bot): await bot.add_cog(AdvancedDefense(bot))
