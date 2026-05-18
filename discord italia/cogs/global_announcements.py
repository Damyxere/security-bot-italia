import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class GlobalAnnouncements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="scorpion_broadcast", description="🚀 CONTROLLO ASSOLUTO: Invia un annuncio DM totalmente personalizzato a tutti")
    @app_commands.describe(
        titolo="Il titolo dell'Embed",
        messaggio="Il testo principale del messaggio",
        colore_hex="Il colore della barra dell'embed (es: #00FBFF per Ciano, #FF0000 per Rosso)",
        immagine_grande="URL dell'immagine centrale grande (Opzionale)",
        miniatura_destra="URL della miniatura piccola in alto a destra (Opzionale)",
        testo_footer="Il testo personalizzato in fondo all'embed (Opzionale)",
        icona_footer="URL della piccola icona tonda accanto al testo del footer (Opzionale)"
    )
    async def broadcast(
        self, 
        interaction: discord.Interaction, 
        titolo: str, 
        messaggio: str, 
        colore_hex: str, 
        immagine_grande: str = None,
        miniatura_destra: str = None,
        testo_footer: str = "Network di Sicurezza Scorpion | Monitoraggio Globale",
        icona_footer: str = None
    ):
        # 🔐 CONTROLLO SUPREMO: Solo tu puoi toccare questo comando
        if interaction.user.id != self.bot.owner_id:
            return await interaction.response.send_message("❌ Accesso Negato. Solo Scorpion ha il controllo totale del Broadcast.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        # 🎨 1. GESTIONE COLORE PERSONALIZZATO
        try:
            hex_clean = colore_hex.lstrip('#')
            colore_embed = discord.Color(int(hex_clean, 16))
        except ValueError:
            colore_embed = discord.Color(0x00FBFF) # Default Ciano Scorpion se sbagli a scrivere

        # 🖼️ 2. COSTRUZIONE EMBED SU MISURA (Controllo Totale)
        embed_broadcast = discord.Embed(
            title=titolo,
            description=messaggio,
            color=colore_embed,
            timestamp=discord.utils.utcnow()
        )
        
        # Gestione Immagine Grande (Corpo centrale)
        if immagine_grande and immagine_grande.startswith("http"):
            embed_broadcast.set_image(url=immagine_grande)
            
        # Gestione Miniatura (In alto a destra, es. logo Scorpion)
        if miniatura_destra and miniatura_destra.startswith("http"):
            embed_broadcast.set_thumbnail(url=miniatura_destra)
            
        # Gestione Footer (Testo + Icona tonda personalizzata)
        if icona_footer and icona_footer.startswith("http"):
            embed_broadcast.set_footer(text=testo_footer, icon_url=icona_footer)
        else:
            embed_broadcast.set_footer(text=testo_footer)

        # 👥 3. RACCOLTA UTENTI UNICI (Anti-Doppione)
        utenti_unici = set()
        for guild in self.bot.guilds:
            for member in guild.members:
                if not member.bot:
                    utenti_unici.add(member)

        await interaction.followup.send(f"🛰️ Configurazione completata. Invio dell'Embed personalizzato a `{len(utenti_unici)}` utenti in corso...", ephemeral=True)

        inviati = 0
        falliti = 0

        # 🚀 4. FLUSSO DI INVIO SICURO (Anti-Ban Discord)
        for utente in utenti_unici:
            try:
                await utente.send(embed=embed_broadcast)
                inviati += 1
                await asyncio.sleep(0.5) # Ritardo di mezzo secondo per non far crashare il token
            except discord.Forbidden:
                falliti += 1
            except Exception:
                falliti += 1

        print(f"[BROADCAST ASSOLUTO] Finito. Consegnati: {inviati} | DM Chiusi: {falliti}")

async def setup(bot):
    await bot.add_cog(GlobalAnnouncements(bot))

