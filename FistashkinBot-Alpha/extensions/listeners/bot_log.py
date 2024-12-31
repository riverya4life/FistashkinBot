import disnake

from disnake.ext import commands
from loguru import logger


class BotLog(commands.Cog):

    hidden = True

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener(disnake.Event.connect)
    async def on_connect(self):
        logger.info(
            f"[BOT CONNECT] Бот присоединился: {self.bot.user.name} ({self.bot.user.id})"
        )
        logger.info(f"[BOT CONNECT] Пинг: {round(self.bot.latency * 1000)}мс")

    @commands.Cog.listener(disnake.Event.disconnect)
    async def on_disconnect(self):
        logger.warning(f"[BOT DISCONNECT] Бот отключен")

    @commands.Cog.listener(disnake.Event.resumed)
    async def on_resumed(self):
        logger.info(f"[BOT RESUMED] Бот подключен")

    @commands.Cog.listener(disnake.Event.shard_connect)
    async def on_shard_connect(self, shard_id: int):
        logger.info(f"[SHARD CONNECT] Шард #{shard_id} подключен")
        logger.info(
            f"[SHARD CONNECT] Пинг: {round(self.bot.get_shard(shard_id).latency * 1000)}мс"
        )

    @commands.Cog.listener(disnake.Event.shard_disconnect)
    async def on_shard_disconnect(self, shard_id: int):
        logger.warning(f"[SHARD DISCONNECT] Шард #{shard_id} отключен")

    @commands.Cog.listener(disnake.Event.shard_resumed)
    async def on_shard_resumed(self, shard_id: int):
        logger.warning(f"[SHARD RESUMED] Шард #{shard_id} подключен")
        logger.warning(
            f"[SHARD RESUMED] Пинг: {round(self.bot.get_shard(shard_id).latency * 1000)}мс"
        )


def setup(bot: commands.Bot):
    bot.add_cog(BotLog(bot))
