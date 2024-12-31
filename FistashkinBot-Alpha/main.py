import disnake
import datetime
import os

from core import Config, FistashkinBot
from classes import *
from loguru import logger

if __name__ == "__main__":
    os.system("@cls||clear")
    data_time = datetime.datetime.now().strftime("%d.%m.%Y %H-%M-%S")
    logger.add(sink=f"./logs/{data_time}.log")

    bot = FistashkinBot()
    bot.i18n.load("./localization")
    bot.load_extensions()

    try:
        bot.run(Config.TOKEN)
    except HTTPException:
        logger.error("Бот временно забанен в Discord из-за наложенного RateLimit!")
        logger.error("Пытаюсь исправить...")
        system("kill 1")
        try:
            bot.run(Config.TOKEN)
        except HTTPException:
            logger.error("Временно запрещен!")
    except Exception as error:
        logger.error(error)
