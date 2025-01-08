import os
import disnake
import datetime

from disnake.ext import commands
from jishaku.modules import find_extensions_in
from loguru import logger
from core import config


class FistashkinBot(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            intents=disnake.Intents.all(),
            command_prefix="f.",
            help_command=None,
            #chunk_guilds_at_startup=False,
            reload=True,
            enable_debug_events=True,
            #test_guilds=[1008029744178143243, 1037792926383747143, 809899167282364416],
            command_sync_flags=commands.CommandSyncFlags(
                sync_commands=True,  # Синхронизировать команды
                sync_commands_debug=True,
            ),  # Флаги синхронизации
            *args,
            **kwargs,
        )
        self.uptime = datetime.datetime.now()
        self.config = config.Config()

    def load_extensions(self):
        for folder in os.listdir("extensions"):
            for cog in find_extensions_in(f"extensions/{folder}"):
                try:
                    self.load_extension(cog)
                    logger.info(f"[LOAD] {cog} загружен!")
                except Exception as e:
                    logger.error(f"[ERROR] {folder}.{cog} навернул говна и упал: {e}")
