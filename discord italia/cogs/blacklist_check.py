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
                description="❌ **ERRORE**: Specifica un ID o tagga un utente.\nEsempio: `!controlla @Scorpion` o `!controlla 123456789`",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed_aiuto)

        # Pulizia dell'input: estrae l'ID se è un tag (es. <@!123...> diventa 123...)
        target_id = re.sub(r'\D', '', target)

        if not target_id:
            return await ctx.send("❌ ID non valido.")

        # Ricerca nel Database
        user_data = db.reference(f'blacklist/users/{target_id}').get()
        server_data = db.reference(f'blacklist/servers/{target_id}').get()
        data = user_data or server_data
        tipo = "UTENTE" if user_data else "SERVER"

        if data:
            # MESSAGGIO FIGO (EMBED AGGRESSIVO)
            embed = discord.Embed(
                title="🚨 RISCONTRO NEL DATABASE GLOBALE",
                description=f"Il soggetto cercato è presente nel sistema di sicurezza **Scorpion Security**.",
                color=0xFF0000 # Rosso puro
            )
            
            embed.set_thumbnail(url="https://i.imgur.com/8E8o5m8.png") # Puoi cambiare questo link con un'icona a forma di scudo o pericolo
            
            embed.add_field(name="👤 SOGGETTO", value=f"```yaml\n{data['nome']}```", inline=True)
            embed.add_field(name="🆔 ID", value=f"```yaml\n{target_id}```", inline=True)
            embed.add_field(name="📂 TIPO", value=f"```yaml\n{tipo}```", inline=True)
            
            embed.add_field(name="❗ GRAVITÀ", value=f"**{data['gravita'].upper()}**", inline=False)
            embed.add_field(name="📝 MOTIVAZIONE", value=f"```fix\n{data['motivo']}```", inline=False)
            
            if data.get('prove') and data['prove'].lower() != "nessuna":
                embed.add_field(name="🔗 PROVE ALLEGATE", value=f"[Clicca qui per visualizzare le prove]({data['prove']})", inline=False)
            else:
                embed.add_field(name="🔗 PROVE ALLEGATE", value="*Nessuna prova pubblica disponibile*", inline=False)

            embed.set_footer(text=f"Data segnalazione: {data['data']} | Scorpion Security Database")
            
            await ctx.send(embed=embed)
        else:
            # MESSAGGIO PULITO (VERDE)
            embed_clean = discord.Embed(
                title="✅ RISULTATO: PULITO",
                description=f"L'ID `{target_id}` non è presente nei nostri archivi.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed_clean)

async def setup(bot):
    await bot.add_cog(CheckCog(bot))
