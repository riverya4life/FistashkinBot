import disnake
import random

from disnake.ext import commands
from utils import constant, enums, main
from loguru import logger

from classes import database as db


class DB_Event(commands.Cog):

    hidden = True

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.otheremojis = constant.OtherEmojis()
        self.color = enums.Color()
        self.economy = main.EconomySystem()
        self.enum = enums.Enum()

    @commands.Cog.listener(disnake.Event.ready)
    async def on_ready(self):
        await db.create_table()

        for guild in self.bot.guilds:
            for member in guild.members:
                await db.insert_new_member(member)

        logger.info(f"[DATABASE] Таблицы успешно созданы!")

    @commands.Cog.listener(disnake.Event.member_join)
    async def on_member_join(self, member):
        await db.insert_new_member(member)

    @commands.Cog.listener(disnake.Event.guild_join)
    async def on_guild_join(self, guild):
        for member in guild.members:
            await db.insert_new_member(member)

    @commands.Cog.listener(disnake.Event.slash_command_completion)
    @commands.Cog.listener(disnake.Event.user_command_completion)
    async def on_command_completion(self, inter: disnake.ApplicationCommandInteraction):
        logger.info(
            f"use: {inter.application_command.qualified_name}, user: {inter.author.name} ({inter.author.id}), guild: {inter.guild.name} ({inter.guild.id})"
        )
        return await db.update_used_commands()


def setup(bot):
    bot.add_cog(DB_Event(bot))
