import discord
from discord.ext import commands
import datetime
from firebase_admin import db

class EliteDefenseEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reaction_tracker = {} # Traccia le reazioni veloci

    # 🚷 1. MODULO ANTI-ALT ACCOUNT
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        is_active = db.reference(f'settings/guilds/{guild_id}/modules/anti_alt').get()
        if not is_active: return

        now = discord.utils.utcnow()
        eta_account = (now - member.created_at).days

        # Se l'account è stato creato da meno di 3 giorni, scatta l'espulsione immediata
        if eta_account < 3:
            try:
                await member.send(f"⚠️ **SICUREZZA**: Sei stato rimosso da **{member.guild.name}** perché il tuo account è troppo nuovo (creato da meno di 3 giorni). Protezione Anti-Alt attiva.")
            except:
                pass
            await member.kick(reason="Scorpion Anti-Alt System: Account creato da meno di 3 giorni.")

    # 🎭 2. MODULO ANTI-SPAM REAZIONI (Emoji Bombing)
    @commands.Cog.listener()
    async def on_message_reaction_add(self, reaction, user):
        if user.bot or not reaction.message.guild: return
        
        guild_id = str(reaction.message.guild.id)
        is_active = db.reference(f'settings/guilds/{guild_id}/modules/anti_reaction').get()
        if not is_active: return

        user_id = user.id
        now = datetime.datetime.now()

        if user_id not in self.reaction_tracker:
            self.reaction_tracker[user_id] = []
        
        self.reaction_tracker[user_id].append(now)
        # Tiene in cache solo le reazioni degli ultimi 4 secondi
        self.reaction_tracker[user_id] = [t for t in self.reaction_tracker[user_id] if (now - t).total_seconds() < 4]

        # Se l'utente inserisce più di 8 reazioni in 4 secondi, viene punito
        if len(self.reaction_tracker[user_id]) > 8:
            try:
                await reaction.message.channel.set_permissions(user, send_messages=False, add_reactions=False)
                await reaction.message.remove_reaction(reaction.emoji, user)
                await reaction.message.channel.send(f"🔇 {user.mention} è stato privato del permesso di reazione e scrittura per Spam di Emoji.", delete_after=10)
            except:
                pass

    # 👁️ 3. GHOST EDIT DETECTOR (Intercetta chi modifica i messaggi per aggirare i filtri)
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot or not after.guild: return
        
        guild_id = str(after.guild.id)
        is_active = db.reference(f'settings/guilds/{guild_id}/modules/anti_edit').get()
        if not is_active: return

        # Se l'utente modifica un messaggio vecchio inserendoci un invito Discord o un link fraudolento
        if "discord.gg/" in after.content.lower() or "http" in after.content.lower():
            if not after.author.guild_permissions.manage_messages:
                await after.delete()
                await after.channel.send(f"⚠️ {after.author.mention}, non puoi aggirare i filtri modificando i messaggi precedenti!", delete_after=5)

async def setup(bot): await bot.add_cog(EliteDefenseEngine(bot))
