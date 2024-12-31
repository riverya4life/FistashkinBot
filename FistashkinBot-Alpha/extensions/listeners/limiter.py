import disnake

from disnake.ext import commands


class Limiter(commands.Cog):

    hidden = True
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener(disnake.Event.guild_join)
    async def on_guild_join(self, guild: disnake.Guild):
        if len(self.bot.guilds) == 100 and not (
            self.bot.user.public_flags.verified_bot
        ):
            guilds = sorted(self.bot.guilds, key=lambda x: x.member_count)
            for guild in guilds:
                if guild.member_count < 99 and len(self.bot.guilds) > 90:
                    await guild.leave()


def setup(bot):
    bot.add_cog(Limiter(bot))
