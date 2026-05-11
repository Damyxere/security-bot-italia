import discord
from discord.ext import commands
from firebase_admin import db

class CheckCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.command(name="controlla")
    async def controlla(self, ctx, target_id: str = None):
        if not target_id:
            return await ctx.send("❓ Inserisci un ID! Esempio: `!controlla 123456789` ")

        user_data = db.reference(f'blacklist/users/{target_id}').get()
        server_data = db.reference(f'blacklist/servers/{target_id}').get()
        data = user_data or server_data

        if data:
            emb = discord.Embed(title="⚠️ RISCONTRO TROVATO NELLA BLACKLIST", color=discord.Color.red())
            emb.add_field(name="Soggetto", value=data['nome'], inline=True)
            emb.add_field(name="Gravità", value=data['gravita'], inline=True)
            emb.add_field(name="Motivo", value=data['motivo'], inline=False)
            emb.add_field(name="Prove", value=data['prove'], inline=False)
            emb.set_footer(text=f"Segnalato da {data['staffer']} il {data['data']}")
            await ctx.send(embed=emb)
        else:
            await ctx.send(f"✅ L'ID `{target_id}` non è presente nel database Scorpion.")

async def setup(bot): await bot.add_cog(CheckCog(bot))
