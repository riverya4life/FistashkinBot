import disnake
import datetime
import asyncio

from disnake.ext import commands
from utils import enums

from classes import database as db


class Logs(commands.Cog):

    hidden = True
    
    def __init__(self, bot):
        self.bot = bot
        self.color = enums.Color()

    @commands.Cog.listener(disnake.Event.member_join)
    async def on_member_join(self, member: disnake.Member):
        log_channel = await db.get_log_channel(guild=member.guild)
        if log_channel is None:
            return
        channel_id = log_channel["log_channel_id"]
        channel = disnake.utils.get(member.guild.channels, id=channel_id)
        if channel is None:
            return
        webhook = None
        webhooks = await channel.webhooks()
        for hook in webhooks:
            if hook.name == "FistashkinLog":
                webhook = hook
                break
        if webhook is None:
            webhook = await channel.create_webhook(name="FistashkinLog")

        registerf = disnake.utils.format_dt(member.created_at, style="f")
        registerr = disnake.utils.format_dt(member.created_at, style="R")
        embed = (
            disnake.Embed(
                description=f"{'Бот' if member.bot else 'Участник'} **{member}** ({member.mention}) присоединился к серверу",
                color=self.color.MAIN,
                timestamp=datetime.datetime.fromtimestamp(
                    datetime.datetime.now().timestamp()
                ),
            )
            .add_field(
                name="Дата регистрации",
                value=f"{registerf} ({registerr})",
                inline=True,
            )
            .set_footer(
                text=f"ID {'бота' if member.bot else 'участника'}: {member.id}"
            )
            .set_thumbnail(url=member.display_avatar.url)
        )
        await webhook.send(
            embed=embed,
            username="FistashkinLog",
            avatar_url=self.bot.user.display_avatar.url,
            allowed_mentions=disnake.AllowedMentions.none(),
        )

    @commands.Cog.listener(disnake.Event.member_remove)
    async def on_member_remove(self, member: disnake.Member):
        log_channel = await db.get_log_channel(guild=member.guild)
        if log_channel is None:
            return
        channel_id = log_channel["log_channel_id"]
        channel = disnake.utils.get(member.guild.channels, id=channel_id)
        if channel is None:
            return
        webhook = None
        webhooks = await channel.webhooks()
        for hook in webhooks:
            if hook.name == "FistashkinLog":
                webhook = hook
                break
        if webhook is None:
            webhook = await channel.create_webhook(name="FistashkinLog")

        roles = int(len(member.roles) - 1)
        role_list = [r.mention for r in member.roles][1:]
        role_list.reverse()
        role_string = " | ".join(role_list)
        embed = (
            disnake.Embed(
                description=f"{'Бот' if member.bot else 'Участник'} **{member}** ({member.mention}) покинул сервер",
                color=self.color.MAIN,
                timestamp=datetime.datetime.fromtimestamp(
                    datetime.datetime.now().timestamp()
                ),
            )
            .add_field(
                name=f"{'Роли' if roles > 1 else 'Роль'} при выходе",
                value=role_string,
                inline=False,
            ) if not member.top_role == member.guild.default_role else None
            .set_footer(
                text=f"ID {'бота' if member.bot else 'участника'}: {member.id}"
            )
            .set_thumbnail(url=member.display_avatar.url)
        )
        await webhook.send(
            embed=embed,
            username="FistashkinLog",
            avatar_url=self.bot.user.display_avatar.url,
            allowed_mentions=disnake.AllowedMentions.none(),
        )

    @commands.Cog.listener(disnake.Event.message_delete)
    async def on_message_delete(self, message: disnake.Member):
        log_channel = await db.get_log_channel(guild=message.guild)
        if log_channel is None:
            return
        channel_id = log_channel["log_channel_id"]
        channel = disnake.utils.get(message.guild.channels, id=channel_id)
        if channel is None:
            return
        webhook = None
        webhooks = await channel.webhooks()
        for hook in webhooks:
            if hook.name == "FistashkinLog":
                webhook = hook
                break
        if webhook is None:
            webhook = await channel.create_webhook(name="FistashkinLog")

        if message.author.bot:
            return

        embed = (
            disnake.Embed(
                description=f"Сообщение было удалено",
                color=self.color.MAIN,
                timestamp=datetime.datetime.fromtimestamp(
                    datetime.datetime.now().timestamp()
                ),
            )
            .add_field(
                name="Сообщение", value=f"```{message.content}```", inline=False
            ) if message.content or len(message.content) < 1024 else None
            .add_field(
                name="Автор",
                value=f"**{message.author.name}** ({message.author.mention})",
                inline=True,
            )
            .add_field(
                name="Канал",
                value=f"**{message.channel.name}** ({message.channel.mention})",
                inline=True,
            )
            .add_field(
                name="Изображение",
                value=f"[Тык]({message.attachments[0].proxy_url})",
                inline=False,
            ) if message.attachments else None
            .set_image(url=message.attachments[0].proxy_url) if message.attachments else None
            .set_footer(text=f"ID сообщения: {message.id}")
            .set_thumbnail(url=message.author.display_avatar.url)
        )
        await webhook.send(
            embed=embed,
            username="FistashkinLog",
            avatar_url=self.bot.user.display_avatar.url,
            allowed_mentions=disnake.AllowedMentions.none(),
        )

    @commands.Cog.listener(disnake.Event.message_edit)
    async def on_message_edit(self, before, after):
        log_channel = await db.get_log_channel(guild=after.guild)
        if log_channel is None:
            return
        channel_id = log_channel["log_channel_id"]
        channel = disnake.utils.get(after.guild.channels, id=channel_id)
        if channel is None:
            return
        webhook = None
        webhooks = await channel.webhooks()
        for hook in webhooks:
            if hook.name == "FistashkinLog":
                webhook = hook
                break
        if webhook is None:
            webhook = await channel.create_webhook(name="FistashkinLog")
        if after.content == before.content:
            return
        elif len(after.content) > 4096 or len(before.content) > 4096:
            return
        elif after.author.bot:
            return

        else:
            embed = (
                disnake.Embed(
                    description=f"[Сообщение]({after.jump_url}) было отредактировано",
                    color=self.color.MAIN,
                    timestamp=datetime.datetime.fromtimestamp(
                        datetime.datetime.now().timestamp()
                    ),
                )
                .add_field(
                    name="Старое содержимое:",
                    value=f"```{before.content}```",
                    inline=False,
                )
                .add_field(
                    name="Новое содержимое:",
                    value=f"```{after.content}```",
                    inline=False,
                )
                .add_field(
                    name="Автор",
                    value=f"**{after.author.name}** ({after.author.mention})",
                    inline=True,
                )
                .add_field(
                    name="Канал",
                    value=f"**{after.channel.name}** ({after.channel.mention})",
                    inline=True,
                )
                .set_footer(text=f"ID сообщения: {after.id}")
                .set_thumbnail(url=after.author.display_avatar.url)
                .set_image(
                    url=after.attachments[0].proxy_url
                    if bool(after.attachments)
                    else disnake.embeds.EmptyEmbed
                ) if after.attachments else None
            )
        await webhook.send(
            embed=embed,
            username="FistashkinLog",
            avatar_url=self.bot.user.display_avatar.url,
            allowed_mentions=disnake.AllowedMentions.none(),
        )

    @commands.Cog.listener(disnake.Event.member_update)
    async def on_member_update(self, before, after):
        log_channel = await db.get_log_channel(guild=after.guild)
        if log_channel is None:
            return
        channel_id = log_channel["log_channel_id"]
        channel = disnake.utils.get(after.guild.channels, id=channel_id)
        if channel is None:
            return
        webhook = None
        webhooks = await channel.webhooks()
        for hook in webhooks:
            if hook.name == "FistashkinLog":
                webhook = hook
                break
        if webhook is None:
            webhook = await channel.create_webhook(name="FistashkinLog")

        embed = (
            disnake.Embed(
                color=self.color.MAIN,
                timestamp=datetime.datetime.fromtimestamp(
                    datetime.datetime.now().timestamp()
                ),
            )
            .set_footer(text=f"ID {'бота' if after.bot else 'участника'}: {after.id}")
            .set_thumbnail(url=after.display_avatar.url)
        )

        if before.display_name != after.display_name:
            embed.description = f"Никнейм {'бота' if after.bot else 'участника'} **{after}** ({after.mention}) был изменен"
            embed.add_field(
                name="Старый никнейм:", value=before.display_name, inline=True
            )
            embed.add_field(
                name="Новый никнейм:", value=after.display_name, inline=True
            )
            await channel.send(embed=embed)

        if before.roles != after.roles:
            added_roles = [
                f"<@&{role.id}>" for role in after.roles if role not in before.roles
            ]
            removed_roles = [
                f"<@&{role.id}>" for role in before.roles if role not in after.roles
            ]

            embed.description = f"Роли {'бота' if after.bot else 'участника'} **{after}** ({after.mention}) были изменены"

            if added_roles:
                for role in added_roles:
                    roles = role
                embed.add_field(
                    name=f"{'Добавленные роли:' if int(len(roles)) > 1 else 'Добавленная роль:'}",
                    value=roles,
                    inline=True,
                )
            if removed_roles:
                for role in removed_roles:
                    roles = role
                embed.add_field(
                    name=f"{'Убранные роли:' if int(len(roles)) > 1 else 'Убранная роль:'}",
                    value=roles,
                    inline=True,
                )
        await webhook.send(
            embed=embed,
            username="FistashkinLog",
            avatar_url=self.bot.user.display_avatar.url,
            allowed_mentions=disnake.AllowedMentions.none(),
        )

    @commands.Cog.listener(disnake.Event.voice_state_update)
    async def on_voice_state_update(
        self,
        member: disnake.Member,
        before: disnake.VoiceState,
        after: disnake.VoiceState,
    ):
        log_channel = await db.get_log_channel(guild=member.guild)
        if log_channel is None:
            return
        channel_id = log_channel["log_channel_id"]
        channel = disnake.utils.get(member.guild.channels, id=channel_id)
        if channel is None:
            return
        webhook = None
        webhooks = await channel.webhooks()
        for hook in webhooks:
            if hook.name == "FistashkinLog":
                webhook = hook
                break
        if webhook is None:
            webhook = await channel.create_webhook(name="FistashkinLog")

        embed = (
            disnake.Embed(
                color=self.color.MAIN,
                timestamp=datetime.datetime.fromtimestamp(
                    datetime.datetime.now().timestamp()
                ),
            )
            .set_footer(
                text=f"ID {'бота' if member.bot else 'участника'}: {member.id}"
            )
            .set_thumbnail(url=member.display_avatar.url)
        )

        if before.channel is None and after.channel is not None:
            embed.description = (
                f"**{member}** ({member.mention}) присоединился к голосовому каналу"
            )
            embed.add_field(
                name="Канал:",
                value=f"**{after.channel}** ({after.channel.mention})",
                inline=True,
            )
        elif before.channel is not None and after.channel is None:
            embed.description = (
                f"**{member}** ({member.mention}) покинул голосовой канал"
            )
            embed.add_field(
                name="Канал:",
                value=f"**{before.channel}** ({before.channel.mention})",
                inline=True,
            )
        elif (
            before.channel is not None
            and after.channel is not None
            and before.channel != after.channel
        ):
            embed.description = (
                f"**{member}** ({member.mention}) перешёл в голосовой канал"
            )
            embed.add_field(
                name="До:",
                value=f"**{before.channel}** ({before.channel.mention})",
                inline=True,
            )
            embed.add_field(
                name="После:",
                value=f"**{after.channel}** ({after.channel.mention})",
                inline=False,
            )
        await webhook.send(
            embed=embed,
            username="FistashkinLog",
            avatar_url=self.bot.user.display_avatar.url,
            allowed_mentions=disnake.AllowedMentions.none(),
        )


def setup(bot):
    bot.add_cog(Logs(bot))
