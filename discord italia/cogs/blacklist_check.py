import discord
from discord.ext import commands
from firebase_admin import db

class CheckCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.command(name="controlla")
    async def controlla(self, ctx, target_id: str = None):
        if not target_id:
            return await ctx.send("❓ Inserisci un ID! Es: `!controlla 12345` ")

        user_data = db.reference(f'blacklist/users/{target_id}').get()
        server_data = db.reference(f'blacklist/servers/{target_id}').get()
        data = user_data or server_data

        if data:
            emb = discord.Embed(title="⚠️ RISCONTRO TROVATO", color=discord.Color.red())
            emb.add_field(name="Nome", value=data['nome'], inline=True)
            emb.add_field(name="Motivo", value=data['motivo'], inline=False)
            emb.add_field(name="Prove", value=data['prove'] or "No link", inline=False)
            emb.set_footer(text=f"By {data['staffer']}")
            await ctx.send(embed=emb)
        else:
            await ctx.send(f"✅ L'ID `{target_id}` è pulito.")

async def setup(bot): await bot.add_cog(CheckCog(bot))