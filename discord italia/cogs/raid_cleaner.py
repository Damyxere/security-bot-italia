import discord
from discord.ext import commands
from discord import app_commands

class RaidCleaner(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="nuke", description="💥 Distruggi e ricrea il canale (Elimina tutto lo spam)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def nuke(self, it: discord.Interaction):
        channel = it.channel
        new_channel = await channel.clone(reason="Nuke Scorpion Security")
        await channel.delete()
        await new_channel.send("💥 **CANALE BONIFICATO**\n*Tutto lo spam è stato eliminato con successo.*")

    @app_commands.command(name="purge_links", description="🧹 Rimuove tutti i messaggi con link (ultimi 100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge_links(self, it: discord.Interaction):
        def is_link(m): return "http" in m.content or "discord.gg" in m.content
        deleted = await it.channel.purge(limit=100, check=is_link)
        await it.response.send_message(f"🧹 Eliminati `{len(deleted)}` messaggi contenenti link sospetti.", ephemeral=True)

async def setup(bot): await bot.add_cog(RaidCleaner(bot))
