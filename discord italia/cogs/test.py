import discord
from discord.ext import commands

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="test")
    async def test(self, ctx):
        # Verifica se chi scrive è Scorpion (l'Owner)
        if ctx.author.id == self.bot.owner_id:
            embed = discord.Embed(
                title="🚀 Sistema Operativo!",
                description="Il bot risponde correttamente ai comandi di Scorpion.",
                color=discord.Color.gold()
            )
            embed.add_field(name="Stato Moduli", value="✅ Cartella `cogs` caricata", inline=False)
            embed.add_field(name="Creatore", value=f"👑 {ctx.author.name}", inline=True)
            embed.set_footer(text="Scorpion Security è pronto alla guerra.")
            
            await ctx.send(embed=embed)
        else:
            # Risposta per tutti gli altri utenti
            await ctx.send(f"❌ Accesso negato. Solo il creatore **Scorpion** può eseguire il test del sistema.")

async def setup(bot):
    await bot.add_cog(Test(bot))