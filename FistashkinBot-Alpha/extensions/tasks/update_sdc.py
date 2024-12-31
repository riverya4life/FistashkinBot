import disnake
import random
import aiohttp

from disnake.ext import commands, tasks
from core import config
from loguru import logger


class UpdateSDCAPI(commands.Cog):

    hidden = True

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = config.Config()

    async def cog_load(self):
        self.sdc_stats.start()

    async def cog_unload(self):
        self.sdc_stats.cancel()

    @tasks.loop(minutes=1)
    async def sdc_stats(self):
        headers = {
            "Authorization": f"SDC {self.config.SDC_TOKEN}",
        }
        data = {
            "servers": len(self.bot.guilds),
            "shards": len(self.bot.shards),
        }
        url = f"https://api.server-discord.com/v2/bots/{self.bot.user.id}/stats"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as resp:
                if resp.status == 200:
                    logger.info("[SDC API] Статистика SDC API успешно отправлена.")
                    await session.close()
                else:
                    logger.error("[SDC API] Ошибка при отправке SDC API статистики.")
                    logger.error(f"[SDC API] Статус код: {resp.status}")
                    logger.error(f"[SDC API] Тело ответа: {await resp.text()}")
                    await session.close()

    @sdc_stats.before_loop
    async def before_sdc_stats(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(UpdateSDCAPI(bot))
