import disnake
import datetime
import uuid

from disnake.ext import commands
from utils import CustomError, Support_Link, enums, main
from loguru import logger

DESCRIPTIONS = {
    commands.MissingPermissions: "❌ У тебя нет прав на выполнения этой команды!",
    commands.BotMissingPermissions: "❌ У бота нет прав на выполнения этой команды!",
    commands.UserNotFound: "❌ Указанный участник не найден. Проверь ID/Тег/Никнейм на правильность.",
    commands.MemberNotFound: "❌ Указанный пользователь не найден., Проверь ID/Тег/Никнейм на правильность.",
    commands.NSFWChannelRequired: "❌ Эта команда доступна только в каналах с пометкой NSFW!",
    commands.NotOwner: "❌ Ты не являешься моим папиком!",
    commands.RoleNotFound: "❌ Указанная роль не найдена.",
    disnake.Forbidden: "❌ У бота нет прав на выполнения этого действия!",
    commands.ChannelNotReadable: "❌ У бота нет прав на просмотр данного канала!",
    commands.BadArgument: "❌ Ты указал неверный аргумент!",
    50013: "❌ У бота нет прав на выполнения этого действия!",
}

PERMISSIONS = {
    "administrator": "Администратор",
    "ban_members": "Банить участников",
    "kick_members": "Выгонять участников",
    "manage_guild": "Управлять сервером",
    "send_messages": "Отправлять сообщения",
    "manage_members": "Управлять участниками",
    "view_channel": "Просматривать канал",
    "manage_roles": "Управлять ролями",
    "moderate_members": "Управлять участниками",
    "manage_messages": "Управлять сообщениями",
    "manage_channels": "Управлять каналами",
}


class OnErrors(commands.Cog):

    hidden = True
    
    def __init__(self, bot):
        self.bot = bot
        self.main = main.MainSettings()
        self.color = enums.Color()

    @commands.Cog.listener(disnake.Event.slash_command_error)
    @commands.Cog.listener(disnake.Event.error)
    async def on_slash_command_error(
        self, inter: disnake.ApplicationCommandInteraction, error: commands.CommandError
    ):
        error = getattr(error, "original", error)
        logger.error(error)
        error_id = str(uuid.uuid4())
        await inter.response.defer(ephemeral=True)
        embed = (
            disnake.Embed(
                title=f"Произошла ошибка",
                color=self.color.RED
            )
            .set_footer(text=f"ID ошибки: {error_id}")
        )
        embed.description = DESCRIPTIONS.get(
            type(error) if not "50013" in str(error) else 50013,
            f"❌ Произошла неизвестная ошибка, пожалуйста, отправь ошибку на [сервер технической поддержки]({self.main.DISCORD_BOT_SERVER})\n```py\n{str(error)}```",
        )
        view = None if isinstance(error, (commands.MissingPermissions, commands.BotMissingPermissions, commands.CommandOnCooldown, commands.NSFWChannelRequired, CustomError)) else Support_Link()

        if isinstance(
            error, (commands.MissingPermissions, commands.BotMissingPermissions)
        ):
            embed.add_field(
                name="Недостающие права",
                value=", ".join(
                    [PERMISSIONS.get(i, i) for i in error.missing_permissions]
                ),
            )

        elif isinstance(error, commands.CommandOnCooldown):
            cooldown_time = datetime.datetime.now() + datetime.timedelta(
                seconds=int(round(error.retry_after))
            )
            dynamic_time = disnake.utils.format_dt(cooldown_time, style="R")
            embed.description = f"⏱️ Ты достиг кулдауна этой команды. Ты сможешь использовать её вновь {dynamic_time}!"

        elif isinstance(error, commands.NSFWChannelRequired):
            channels = list(
                map(
                    lambda n: n.mention,
                    filter(lambda x: x.nsfw, inter.guild.text_channels),
                )
            )
            channel_list = " ".join(channels)
            if len(channels) != 0:
                embed.add_field(
                    name="Поэтому воспользуйся одним из NSFW-каналов:",
                    value=channel_list,
                )

        elif isinstance(error, CustomError):
            embed.description = f"{error}"

        channel = self.bot.get_channel(1209733432632938506)
        timestamp = int(datetime.datetime.timestamp(datetime.datetime.now()))
        command = inter.permissions.value
        name = inter.application_command.qualified_name
        error_embed = (
            disnake.Embed(
                description=f"`💔` <t:{timestamp}:f> (<t:{timestamp}:R>) Последний вызов вызвал исключение:\n```cmd\n{error}\n```"
                f"\n**Код разрешений:** \n```\n{command}\n```\n**Сервер:** {inter.guild.name} `[ID: {inter.guild.id}]`\n**Пользователь:** {inter.author.name} `[ID: {inter.author.id}]`"
                f"\n**Команда:** </{name}:{inter.data.id}>",
                color=self.color.RED,
            )
            .set_footer(text=f"ID ошибки: {error_id}")
        )
        await channel.send(embed=error_embed)
        await inter.edit_original_message(embed=embed, view=view)


def setup(bot):
    bot.add_cog(OnErrors(bot))
