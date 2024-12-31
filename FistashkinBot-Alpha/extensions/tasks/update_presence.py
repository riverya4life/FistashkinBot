import disnake
import random

from disnake.ext import commands, tasks
from contextlib import suppress
from utils import BotActivity


class UpdatePresenceCog(commands.Cog):

    hidden = True
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        self.update_presence.start()

    async def cog_unload(self):
        self.update_presence.cancel()

    @tasks.loop(minutes=30)
    async def update_presence(self):
        for shard in range(len(self.bot.shards)):
            with suppress(Exception):
                await self.bot.change_presence(
                    activity=random.choice(BotActivity.ACTIVITY),
                    status=disnake.Status.idle,
                    shard_id=shard,
                )

    @update_presence.before_loop
    async def before_update_presence(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(UpdatePresenceCog(bot))
