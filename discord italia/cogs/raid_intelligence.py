import discord
from discord.ext import commands
from discord import app_commands

class RaidIntelligence(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="scan_raid", description="🔍 Scansiona il server per account sospetti")
    @app_commands.checks.has_permissions(kick_members=True)
    async def scan(self, it: discord.Interaction):
        sospetti = []
        now = discord.utils.utcnow()
        for m in it.guild.members:
            # Account creato meno di 3 giorni fa e senza immagine profilo
            if (now - m.created_at).days < 3 and m.display_avatar.url == m.default_avatar.url:
                sospetti.append(f"{m.mention} (`{m.id}`)")
        
        embed = discord.Embed(title="🔍 REPORT SCANSIONE MINACCE", color=0xFFA500)
        if sospetti:
            embed.description = "Trovati account ad alto rischio raid:\n" + "\n".join(sospetti[:10])
            embed.add_field(name="Totale Sospetti", value=str(len(sospetti)))
        else:
            embed.description = "✅ Nessuna minaccia immediata rilevata."
        
        await it.response.send_message(embed=embed)

async def setup(bot): await bot.add_cog(RaidIntelligence(bot))
