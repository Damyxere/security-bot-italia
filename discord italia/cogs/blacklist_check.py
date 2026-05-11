import discord
from discord.ext import commands
from firebase_admin import db
import re

class CheckCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="controlla")
    async def controlla(self, ctx, target: str = None):
        if not target:
            embed_aiuto = discord.Embed(
                description="❌ **ERRORE CRITICO**: Specifica un ID o tagga un utente.\nEsempio: `!controlla @Scorpion` o `!controlla 123456789`",
                color=0xFF0000
            )
            return await ctx.send(embed=embed_aiuto)

        # Pulizia dell'input: estrae l'ID se è un tag
        target_id = re.sub(r'\D', '', target)

        if not target_id:
            return await ctx.send("❌ ID non valido.")

        # Iniziamo la ricerca...
        messaggio_attesa = await ctx.send(f"🔍 *Interrogazione Databank Scorpion Security per ID:* `{target_id}`...")

        # Ricerca nel Database
        user_data = db.reference(f'blacklist/users/{target_id}').get()
        server_data = db.reference(f'blacklist/servers/{target_id}').get()
        data = user_data or server_data
        
        await messaggio_attesa.delete() # Rimuoviamo il messaggio di attesa

        if data:
            # --- COSTRUZIONE MESSAGGIO "FIGO" E MISTERIOSO ---
            
            # 1. Determiniamo il tag da mostrare (se utente)
            tipo_minaccia = "👤 UTENTE" if user_data else "🖥️ SERVER"
            display_target = f"<@{target_id}>" if user_data else f"`{data['nome']}` (Server ID)"

            # 2. Formattazione Gravità (Molto più figa con icone)
            grav = data['gravita'].lower()
            if any(x in grav for x in ["estrema", "critica", "rosso", "10", "9"]):
                grav_display = "🔴 **[ LIVELLO: ESTREMO ]** 🔴\n*Pericolo immediato, isolare il soggetto.*"
                embed_color = 0x720913 # Rosso scuro sangue
            elif any(x in grav for x in ["alta", "alto", "arancione", "8", "7"]):
                grav_display = "🟠 **[ LIVELLO: ALTO ]** 🟠\n*Soggetto instabile, procedere con cautela.*"
                embed_color = 0xff8c00 # Arancione scuro
            else:
                grav_display = "🟡 **[ LIVELLO: MEDIO/BASSO ]** 🟡\n*Soggetto sotto osservazione.*"
                embed_color = 0xffd700 # Oro

            # Create Embed
            embed = discord.Embed(
                title="⚠️ S.C.O.R.P.I.O.N. DATABANK - Rilevamento Minaccia",
                description="***PROTOCOLLO SICUREZZA ATTIVO. LETTURA DOSSIER IN CORSO...***",
                color=embed_color
            )
            
            # --- Logo del BOT in alto a destra (Thumbnail) ---
            if ctx.bot.user.display_avatar:
                embed.set_thumbnail(url=ctx.bot.user.display_avatar.url)
            
            # --- Campi con formattazione aggressiva ---
            
            # Campo SOGGETTO (con il Tag che hai fatto tu)
            embed.add_field(name="🎯 SOGGETTO IDENTIFICATO", value=f"**{display_target}**", inline=False)
            
            embed.add_field(name="🆔 ID SISTEMA", value=f"`{target_id}`", inline=True)
            embed.add_field(name="📂 CLASSIFICAZIONE", value=f"`{tipo_minaccia}`", inline=True)
            
            # Campo GRAVITÀ (Super figo)
            embed.add_field(name="💀 VALUTAZIONE PERICOLO", value=grav_display, inline=False)
            
            # Campo MOTIVAZIONE (Stile dossier con nome originale incluso)
            motivazione_fancy = (
                f"**Nome Registrato in Archivio:** `{data['nome']}`\n\n"
                f"```fix\n[INIZIO TRASCRIZIONE INCIDENTE]\n{data['motivo']}\n[FINE TRASCRIZIONE]```"
            )
            embed.add_field(name="🗒️ DOSSIER ATTIVITÀ", value=motivazione_fancy, inline=False)
            
            # Campo PROVE (Elegante)
            if data.get('prove') and data['prove'].lower() != "nessuna":
                embed.add_field(name="🔗 ARCHIVIO PROVE", value=f"[>>> APRI COLLEGAMENTO ESTERNO <<<]({data['prove']})", inline=False)
            else:
                embed.add_field(name="🔗 ARCHIVIO PROVE", value="*Nessun dato multimediale allegato al dossier.*", inline=False)

            # Footer misterioso
            embed.set_footer(text=f"Generato il: {data['data']} | Protocollo: SCN-DB-{target_id[:5]}", icon_url="https://i.imgur.com/8E8o5m8.png") # Manteniamo l'icona scorpion piccola nel footer
            
            await ctx.send(embed=embed)
        else:
            # MESSAGGIO PULITO (Stile "Nessuna Minaccia")
            embed_clean = discord.Embed(
                title="✅ SCANSIONE COMPLETATA: NESSUN RISCONTRO",
                description=f"L'ID `{target_id}` non è registrato nel Databank Globale Scorpion Security.",
                color=0x00FF00 # Verde brillante
            )
            embed_clean.set_footer(text="Database Aggiornato | Stato: Protetto")
            await ctx.send(embed=embed_clean)

async def setup(bot):
    await bot.add_cog(CheckCog(bot))
