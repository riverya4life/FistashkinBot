import disnake
import datetime

from disnake.ext import commands
from utils import enums, CustomError
from classes import database as db


class ModerationHelper:
    def __init__(self):
        self.color = enums.Color()

    async def check_time_muted(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member,
        time: str,
        reason: str,
        send_to_member: bool = False,
    ):
        if member == inter.author:
            raise CustomError("❌ Ты не можешь применить эту команду на самого себя!")

        if member.bot or member == self.bot.user:
            raise CustomError(f"❌ Ты не можешь применить эту команду на бота {member.mention}!")

        if (
            member.top_role.position >= inter.author.top_role.position
            or member.top_role.position >= inter.guild.me.top_role.position
            or inter.guild.owner == member
        ) and inter.author != inter.guild.owner:
            raise CustomError(
                "❌ Ты не можешь применить данную команду на участников, чья роль выше либо равна твоей!"
            )

        if member.current_timeout:
            raise CustomError(f"❌ Участник {member.mention} уже находится в тайм-ауте!")

        time_units = {
            "s": "seconds", 
            "м": "minutes", "х": "minutes", "m": "minutes",
            "ч": "hours", "г": "hours", "h": "hours",
            "д": "days", "d": "days"
        }

        unit = time[-1].lower()
        duration = int(time[:-1])

        if unit not in time_units or duration <= 0:
            raise CustomError("❌ Указано некорректное время!")

        if (
            (unit in ["s", "с"] and duration > 2419200)
            or (unit in ["m", "м", "х"] and duration > 40320)
            or (unit in ["h", "ч", "г"] and duration > 672)
            or (unit in ["d", "д"] and duration > 28)
        ):
            raise CustomError("❌ Ты не можешь замутить участника больше чем на **28 дней**!")


        dynamic_durations = datetime.datetime.now() + datetime.timedelta(**{time_units[unit]: duration})

        await inter.response.defer(ephemeral=False)

        dynamic_time = disnake.utils.format_dt(dynamic_durations, style="R")

        embed = (
            disnake.Embed(
                description=f"✅ Участник {member.mention} замьючен! 🙊",
                color=self.color.MAIN,
                timestamp=inter.created_at,
            )
            .add_field(name="Модератор", value=inter.author.mention, inline=True)
            .add_field(name="Наказание будет снято", value=dynamic_time, inline=True)
            .add_field(name="Причина", value=reason, inline=False)
            .set_thumbnail(url=member.display_avatar.url)
            .set_footer(
                text="Команда по безопасности Discord сервера",
                icon_url=inter.guild.icon.url if inter.guild.icon else None,
            )
        )

        dm_embed = (
            disnake.Embed(
                description=f"Вам была выдана заглушка чата на сервере `{inter.guild.name}`!",
                color=self.color.MAIN,
                timestamp=inter.created_at,
            )
            .add_field(
                name="Модератор",
                value=f"{inter.author.mention}\n`[ID: {inter.author.id}]`",
                inline=True,
            )
            .add_field(name="Наказание будет снято", value=dynamic_time, inline=True)
            .add_field(name="Причина", value=reason, inline=False)
            .set_thumbnail(url=member.display_avatar.url)
            .set_footer(
                text="Команда по безопасности Discord сервера",
                icon_url=inter.guild.icon.url if inter.guild.icon else None,
            )
        )

        log_channel = await db.get_log_channel(inter.guild)
        if log_channel:
            channel = disnake.utils.get(inter.guild.channels, id=log_channel["log_channel_id"])
            if channel:
                log_embed = (
                    disnake.Embed(
                        description=f"Участник {member.mention} замьючен! 🙊",
                        color=self.color.MAIN,
                        timestamp=inter.created_at,
                    )
                    .add_field(name="Модератор", value=inter.author.mention, inline=True)
                    .add_field(name="Наказание будет снято", value=dynamic_time, inline=True)
                    .add_field(name="Причина", value=reason, inline=False)
                    .set_thumbnail(url=member.display_avatar.url)
                    .set_footer(
                        text=f"ID {'бота' if member.bot else 'участника'}: {member.id}"
                    )
                )
                await channel.send(embed=log_embed)

        await member.timeout(until=dynamic_durations, reason=reason)

        if send_to_member:
            try:
                await member.send(
                    embed=dm_embed,
                    components=[
                        disnake.ui.Button(
                            label=f"Отправлено с {inter.guild.name}",
                            emoji="📨",
                            style=disnake.ButtonStyle.gray,
                            disabled=True,
                        )
                    ],
                )
            except disnake.Forbidden:
                embed.set_footer(text="Участник не получил сообщение о исключении!")

        await inter.edit_original_message(embed=embed)


    async def send_embed_punishment(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member,
        reason: str,
        punish: str,
        dm_punish: str,
        send_to_member: bool = False,
    ):
        if member == inter.author:
            raise CustomError("❌ Ты не можешь применить эту команду на самого себя!")

        if member.bot or member == self.bot.user:
            raise CustomError(f"❌ Ты не можешь применить эту команду на бота {member.mention}!")

        if (
            member.top_role.position >= inter.author.top_role.position
            or member.top_role.position >= inter.guild.me.top_role.position
            or inter.guild.owner == member
        ) and inter.author != inter.guild.owner:
            raise CustomError(
                "❌ Ты не можешь применить данную команду на участников, чья роль выше либо равна твоей!"
            )

        await inter.response.defer(ephemeral=False)

        embed = (
            disnake.Embed(
                description=punish,
                color=self.color.MAIN,
                timestamp=inter.created_at,
            )
            .add_field(name="Модератор", value=inter.author.mention)
            .add_field(name="Причина", value=reason)
            .set_thumbnail(url=member.display_avatar.url)
            .set_footer(
                text="Команда по безопасности Discord сервера",
                icon_url=inter.guild.icon.url if inter.guild.icon else None,
            )
        )

        dm_embed = (
            disnake.Embed(
                description=dm_punish,
                color=self.color.MAIN,
                timestamp=inter.created_at,
            )
            .add_field(
                name="Модератор",
                value=f"{inter.author.mention}\n`[ID: {inter.author.id}]`",
            )
            .add_field(name="Причина", value=reason)
            .set_footer(
                text="Команда по безопасности Discord сервера",
                icon_url=inter.guild.icon.url if inter.guild.icon else None,
            )
        )

        if send_to_member:
            try:
                await member.send(
                    embed=dm_embed,
                    components=[
                        disnake.ui.Button(
                            label=f"Отправлено с {inter.guild.name}",
                            emoji="📨",
                            style=disnake.ButtonStyle.gray,
                            disabled=True,
                        )
                    ],
                )
            except disnake.Forbidden:
                embed.set_footer(text="Участник не получил сообщение о наказании!")

        actions = {
            "ban": {
                "action": inter.guild.ban,
                "args": {"user": member, "reason": reason},
                "message": f"✅ Участник {member.mention} был забанен.",
            },
            "kick": {
                "action": inter.guild.kick,
                "args": {"user": member, "reason": reason},
                "message": f"✅ Участник {member.mention} был изгнан с сервера.",
            },
            "timeout": {
                "action": member.timeout,
                "args": {"until": None, "reason": reason},
                "message": f"✅ С участника {member.mention} сняты ограничения! 🐵",
            },
            "warn": {
                "action": db.add_warn,
                "args": {"member": member, "moderator": inter.author, "reason": reason},
                "message": f"✅ Участник {member.mention} получил предупреждение!",
            },
        }

        for action_key, action_info in actions.items():
            if punish == action_info["message"]:
                if isinstance(action_info["args"], dict):
                    await action_info["action"](**action_info["args"])
                else:
                    await action_info["action"](*action_info["args"])
                print(action_info["message"])
                break


        log_channel = await db.get_log_channel(inter.guild)
        if log_channel:
            channel = disnake.utils.get(inter.guild.channels, id=log_channel["log_channel_id"])
            if channel:
                log_embed = (
                    disnake.Embed(
                        description=punish[2:],
                        color=self.color.MAIN,
                        timestamp=inter.created_at,
                    )
                    .add_field(name="Модератор", value=inter.author.mention)
                    .add_field(name="Причина", value=reason)
                    .set_thumbnail(url=member.display_avatar.url)
                    .set_footer(
                        text=f"ID {'бота' if member.bot else 'участника'}: {member.id}"
                    )
                )
                await channel.send(embed=log_embed)

        await inter.edit_original_message(embed=embed)

